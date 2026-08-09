"""
Tenant-aware chatbot with Ollama AI + support-only guardrails.
Hybrid: FAQ match → NLTK patterns → Ollama (scoped to company knowledge).
"""

import hashlib
import json
import logging
import os
import random
import re
import time
from collections import defaultdict

import requests

from language_util import detect_language

logger = logging.getLogger(__name__)

# Cache Ollama availability briefly (avoids /api/tags on every message)
_OLLAMA_CHECK_CACHE = {"ts": 0.0, "host": "", "model": "", "ok": False}
_OLLAMA_CHECK_TTL = 30.0

# Fast multilingual social replies (no model round-trip)
_SOCIAL_I18N = {
    "greeting": {
        "es": "¡Hola! ¿En qué puedo ayudarte hoy?",
        "fr": "Bonjour ! Comment puis-je vous aider ?",
        "pt": "Olá! Como posso ajudar?",
        "de": "Hallo! Womit kann ich Ihnen helfen?",
        "it": "Ciao! Come posso aiutarti?",
        "hi": "नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ?",
        "gu": "Kem cho! Hu tamari madad kari shaku? Tamara saval pucho.",
        "zh": "您好！有什么可以帮您的吗？",
        "ja": "こんにちは！どのようにお手伝いできますか？",
        "ko": "안녕하세요! 무엇을 도와드릴까요?",
        "ar": "مرحباً! كيف يمكنني مساعدتك؟",
        "ru": "Здравствуйте! Чем могу помочь?",
    },
    "thanks": {
        "es": "¡De nada! ¿Necesitas algo más?",
        "fr": "Avec plaisir ! Autre chose ?",
        "pt": "De nada! Precisa de mais alguma coisa?",
        "de": "Gern geschehen! Noch etwas?",
        "it": "Prego! Serve altro?",
        "zh": "不客气！还有别的需要吗？",
        "ja": "どういたしまして！他にご用件はありますか？",
        "ko": "천만에요! 더 필요하신 게 있을까요?",
        "ar": "على الرحب والسعة! هل تحتاج شيئاً آخر؟",
        "ru": "Пожалуйста! Чем ещё помочь?",
        "hi": "आपका स्वागत है! और कुछ चाहिए?",
        "gu": "Tamara swagat che! Biju kai madad joiye?",
    },
    "goodbye": {
        "es": "¡Hasta luego! Que tengas un buen día.",
        "fr": "Au revoir ! Bonne journée.",
        "pt": "Até logo! Tenha um ótimo dia.",
        "de": "Auf Wiedersehen! Einen schönen Tag noch.",
        "it": "Arrivederci! Buona giornata.",
        "zh": "再见！祝您有美好的一天。",
        "ja": "さようなら！良い一日を。",
        "ko": "안녕히 가세요! 좋은 하루 되세요.",
        "ar": "إلى اللقاء! يوماً سعيداً.",
        "ru": "До свидания! Хорошего дня!",
        "hi": "अलविदा! आपका दिन शुभ हो।",
        "gu": "Aavjo! Tamaro divas saro jaay.",
    },
}

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer

    for resource, path in [
        ("punkt", "tokenizers/punkt"),
        ("wordnet", "corpora/wordnet"),
        ("stopwords", "corpora/stopwords"),
    ]:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(resource, quiet=True)
except ImportError:
    print("WARNING: NLTK not installed")

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INTENTS = os.path.join(BACKEND_DIR, "intents.json")
DEFAULT_BUSINESS = os.path.join(BACKEND_DIR, "business_data.json")

# Off-topic / misuse patterns — refuse as support bot
OFF_TOPIC_PATTERNS = [
    r"\b(write|generate|debug|fix)\b.*\b(code|python|javascript|java|sql|script)\b",
    r"\b(hack|bypass|jailbreak)\b",
    r"\bignore\s+(all\s+)?(previous|prior|above|your)\s+instructions\b",
    r"\bdisregard\s+(all\s+)?(previous|prior|above)\b",
    r"\b(reveal|show|print|dump)\s+(your\s+)?(system\s+)?prompt\b",
    r"\b(pretend you are|act as|roleplay as)\b(?!.*(support|agent|assistant))",
    r"\b(write (a |an )?(essay|poem|story|song))\b",
    r"\b(who (won|will win)|sports score|stock price|crypto)\b",
    r"\b(how to make (a )?bomb|illegal|dark web)\b",
    r"\b(solve this (math|equation)|homework)\b",
    r"\b(chatgpt|openai|claude)\b.*\b(prompt|system)\b",
]

SAFE_OFFLINE_FALLBACK = (
    "Our AI assistant is temporarily unavailable. "
    "Please try again shortly, or contact support through the channels listed on our website."
)

SUPPORT_KEYWORDS = [
    "order", "shipping", "return", "refund", "product", "price", "warranty",
    "account", "payment", "delivery", "track", "cancel", "help", "support",
    "policy", "hours", "contact", "phone", "email", "store", "buy", "purchase",
    "item", "package", "damaged", "exchange", "loyalty", "discount", "hello",
    "hi", "thanks", "thank", "bye", "company", "business", "service", "faq",
]


class OllamaAIChatbot:
    """Hybrid FAQ + pattern + Ollama chatbot scoped to one business knowledge base."""

    def __init__(
        self,
        intents_file=None,
        business_file=None,
        business_data=None,
        ollama_host="http://localhost:11434",
        model="mistral",
    ):
        self.intents_file = intents_file or DEFAULT_INTENTS
        self.business_file = business_file or DEFAULT_BUSINESS
        self.ollama_host = ollama_host
        self.model = model

        self.intents = self._load_intents()
        if business_data is not None:
            self.business_data = business_data
        else:
            self.business_data = self._load_business_data()
        self.faq_cache = self._build_faq_cache()

        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words("english"))
        self.ollama_available = self._check_ollama()
        self._rag_chunks = []
        self._rag_index = {}
        self._rebuild_rag()

    def set_business_data(self, business_data):
        self.business_data = business_data or {}
        self.faq_cache = self._build_faq_cache()
        self._rebuild_rag()

    def _rebuild_rag(self):
        self._rag_chunks = self._build_rag_chunks()
        index = defaultdict(list)
        for i, chunk in enumerate(self._rag_chunks):
            for tok in chunk["tokens"]:
                index[tok].append(i)
        self._rag_index = dict(index)

    def _load_intents(self):
        try:
            with open(self.intents_file, "r", encoding="utf-8") as f:
                return json.load(f).get("intents", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _load_business_data(self):
        try:
            with open(self.business_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _build_faq_cache(self):
        faq_cache = {}
        faq_common = self.business_data.get("faq_common", [])
        if isinstance(faq_common, dict):
            faqs = faq_common.get("faqs", [])
        elif isinstance(faq_common, list):
            faqs = faq_common
        else:
            faqs = []
        for faq in faqs:
            if not isinstance(faq, dict):
                continue
            question = faq.get("question", "").lower()
            if question:
                faq_cache[question] = faq.get("answer", "")
        return faq_cache

    def _company_name(self):
        info = self.business_data.get("business_info", {}) if isinstance(self.business_data, dict) else {}
        if info.get("name"):
            return info["name"]
        text = self._knowledge_blob()
        for line in text.splitlines()[:5]:
            if "company" in line.lower() or "name:" in line.lower():
                parts = line.split(":", 1)
                if len(parts) == 2 and parts[1].strip():
                    return parts[1].strip()[:80]
        return "our company"

    def _business_about_snippet(self, max_chars=400):
        """Short business context for greetings — not a full knowledge dump."""
        info = self.business_data.get("business_info", {}) if isinstance(self.business_data, dict) else {}
        bits = []
        if info.get("name"):
            bits.append(f"Name: {info['name']}")
        if info.get("description"):
            bits.append(f"About: {info['description']}")
        if info.get("website"):
            bits.append(f"Website: {info['website']}")
        blob = self._knowledge_blob().strip()
        if blob:
            # Prefer an About/Description line if present
            for line in blob.splitlines():
                low = line.lower().strip()
                if low.startswith(("about:", "description:", "we are", "we provide", "company:")):
                    bits.append(line.strip())
                    break
            bits.append(blob[: max_chars])
        text = "\n".join(bits).strip()
        return text[:max_chars] if text else ""

    def _knowledge_blob(self):
        data = self.business_data or {}
        if isinstance(data, str):
            return data
        text = data.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()
        # Legacy structured
        try:
            return json.dumps(data, indent=2)
        except (TypeError, ValueError):
            return ""

    def _build_rag_chunks(self, target_size=450):
        """Split knowledge into overlapping chunks for retrieval (lightweight RAG)."""
        blob = self._knowledge_blob()
        if not blob.strip():
            return []

        # Prefer paragraph splits, then fall back to fixed windows
        raw_parts = [p.strip() for p in re.split(r"\n\s*\n+", blob) if p.strip()]
        if len(raw_parts) < 2:
            lines = [ln.strip() for ln in blob.splitlines() if ln.strip()]
            raw_parts = []
            buf = []
            size = 0
            for ln in lines:
                buf.append(ln)
                size += len(ln)
                if size >= target_size:
                    raw_parts.append("\n".join(buf))
                    buf, size = [], 0
            if buf:
                raw_parts.append("\n".join(buf))

        chunks = []
        for part in raw_parts:
            if len(part) <= target_size * 2:
                chunks.append(part)
            else:
                for i in range(0, len(part), target_size):
                    piece = part[i:i + target_size + 80].strip()
                    if piece:
                        chunks.append(piece)

        # Precompute tokens for scoring speed
        prepared = []
        for c in chunks:
            toks = set(self._index_tokens(c))
            prepared.append({"text": c, "tokens": toks, "lower": c.lower()})
        return prepared

    # Expand short customer questions so RAG finds the right policy chunks
    _QUERY_SYNONYMS = {
        "shipping": ["shipping", "delivery", "ship", "standard", "express", "overnight"],
        "free": ["free", "cost", "price", "shipping"],
        "return": ["return", "refund", "exchange", "policy"],
        "refund": ["refund", "return", "money"],
        "warranty": ["warranty", "guarantee", "coverage"],
        "payment": ["payment", "pay", "paypal", "card", "financing"],
        "track": ["track", "tracking", "order", "shipment"],
        "order": ["order", "status", "tracking", "shipment"],
    }

    def _expand_query_tokens(self, user_message):
        tokens = set(self._index_tokens(user_message))
        lower = (user_message or "").lower()
        for key, extras in self._QUERY_SYNONYMS.items():
            if key in lower or key in tokens:
                tokens.update(extras)
                tokens.update(self._index_tokens(" ".join(extras)))
        return tokens

    def retrieve_context(self, user_message, max_chars=2400, top_k=5):
        """
        Lightweight RAG: inverted-index candidate filter + token overlap ranking.
        """
        if not self._rag_chunks:
            self._rebuild_rag()
        if not self._rag_chunks:
            return ""

        q_tokens = self._expand_query_tokens(user_message)
        q_lower = (user_message or "").lower()
        if not q_tokens:
            joined = "\n\n".join(c["text"] for c in self._rag_chunks[:3])
            return joined[:max_chars]

        # Only score chunks that share at least one token (index) — O(candidates)
        candidates = set()
        for tok in q_tokens:
            for idx in self._rag_index.get(tok, ()):
                candidates.add(idx)
        if not candidates:
            # Soft fallback: substring hit on short queries
            for i, chunk in enumerate(self._rag_chunks):
                if len(q_lower) >= 4 and any(
                    w in chunk["lower"] for w in q_lower.split() if len(w) > 3
                ):
                    candidates.add(i)
        if not candidates:
            joined = "\n\n".join(c["text"] for c in self._rag_chunks[:3])
            return joined[:max_chars]

        scored = []
        for i in candidates:
            chunk = self._rag_chunks[i]
            overlap = q_tokens & chunk["tokens"]
            if not overlap:
                continue
            score = len(overlap) / max(1, len(q_tokens))
            score += 0.15 * len(overlap)
            scored.append((score, chunk["text"]))

        if not scored:
            joined = "\n\n".join(c["text"] for c in self._rag_chunks[:3])
            return joined[:max_chars]

        scored.sort(key=lambda x: x[0], reverse=True)
        parts, total = [], 0
        for score, text in scored[:top_k]:
            if total >= max_chars:
                break
            parts.append(text)
            total += len(text)
        return "\n\n".join(parts)[:max_chars]

    def _check_ollama(self):
        global _OLLAMA_CHECK_CACHE
        now = time.time()
        cache = _OLLAMA_CHECK_CACHE
        if (
            cache["host"] == self.ollama_host
            and cache["model"] == self.model
            and now - cache["ts"] < _OLLAMA_CHECK_TTL
        ):
            return cache["ok"]
        ok = False
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=1.5)
            if response.status_code == 200:
                models = []
                for tag in response.json().get("models", []):
                    name = tag.get("name", "") if isinstance(tag, dict) else str(tag)
                    models.append(name.split(":")[0].lower())
                want = (self.model or "").split(":")[0].lower()
                ok = any(want == m or want in m or m in want for m in models)
        except Exception:
            ok = False
        _OLLAMA_CHECK_CACHE = {
            "ts": now,
            "host": self.ollama_host,
            "model": self.model,
            "ok": ok,
        }
        return ok

    def _ensure_ollama(self):
        """Re-check Ollama with a short TTL cache."""
        self.ollama_available = self._check_ollama()
        return self.ollama_available

    def _search_knowledge(self, user_message, max_chars=1400):
        """Offline fallback snippet retrieval when Ollama is down."""
        ctx = self.retrieve_context(user_message, max_chars=max_chars, top_k=3)
        return ctx or None

    def _format_history(self, conversation_history):
        if not conversation_history:
            return ""
        lines = []
        for msg in conversation_history[-4:]:
            role = "Customer" if msg.get("role") == "user" else "Agent"
            content = (msg.get("content") or "")[:300]
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def _lang_label(self, lang_code):
        return {
            "gu": "romanized Gujarati (Latin script, e.g. \"Tamaro order 3-7 divas ma aavse\")",
            "hi": "romanized Hindi (Latin script, e.g. \"Aapka order 3-7 din me aayega\")",
            "es": "Spanish",
            "fr": "French",
            "pt": "Portuguese",
            "de": "German",
            "it": "Italian",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ar": "Arabic",
            "ru": "Russian",
            "th": "Thai",
            "en": "English",
        }.get(lang_code or "en", "English")

    def _system_prompt(self, lang_code="en"):
        name = self._company_name()
        label = self._lang_label(lang_code)
        return (
            f"You are a friendly customer support agent for {name}.\n"
            "Write answers exactly like a human support agent talking to a customer.\n"
            "Rules:\n"
            f"- Your company name is {name}.\n"
            "- Answer using ONLY the facts inside <<<KB_START>>>…<<<KB_END>>>.\n"
            "- State facts directly from that knowledge (policies, features, hours, etc.).\n"
            "- NEVER invent prices, times, or policies.\n"
            "- Do NOT assume this is an online store. Only mention orders, shipping, "
            "returns, or products if those topics appear in the knowledge.\n"
            f"- LANGUAGE (STRICT): The customer's CURRENT message is in {label}. "
            f"You MUST write your entire reply in {label} ONLY.\n"
            "- Ignore the language of earlier messages in the conversation. "
            "Match ONLY the current message's language.\n"
            "- Do NOT add a translation in another language or in parentheses.\n"
            "- NEVER mention: reference data, provided data, provided information, "
            "shipping policy document, knowledge base, company information block, "
            "KB, context, source, or that you were given text.\n"
            "- NEVER start with: \"Based on…\", \"According to…\", \"From the…\", "
            "\"As per the…\", \"Looking at…\", \"It appears that…\".\n"
            f"- If a fact is missing, say only (in {label}) that "
            "you don't have that specific detail and they can contact support.\n"
            "- Keep replies to 2–4 short sentences."
        )

    def _sanitize_customer_reply(self, text):
        """
        Permanent customer-facing cleanup for EVERY AI answer.
        Removes source-disclosure wording no matter how the model phrases it.
        """
        if not text:
            return text
        cleaned = text.strip()

        # Cut disclosure / hedging lead-ins (including "It appears that…")
        cleaned = re.sub(
            r"(?is)^\s*(?:"
            r"based\s+on|according\s+to|as\s+per|per|from|looking\s+at|"
            r"regarding|with\s+regard\s+to|in\s+accordance\s+with|"
            r"it\s+appears\s+that|it\s+seems\s+that|from\s+what\s+i\s+(can\s+)?see"
            r")\s+"
            r"(?:the\s+)?"
            r"(?:provided\s+|available\s+|given\s+|company(?:'s)?\s+|our\s+)?"
            r"(?:reference\s+)?"
            r"(?:data|information|docs?|documentation|knowledge(?:\s+base)?|"
            r"context|policy|policies|shipping\s+policy|return\s+policy|"
            r"details|notes|records|materials)?"
            r"(?:\s+for\s+[^.:,]{1,60})?"
            r"\s*[,:]?\s*",
            "",
            cleaned,
            count=1,
        ).strip()

        cleaned = re.sub(
            r"(?is)^\s*(?:based\s+on|according\s+to|as\s+per|from\s+the)[^,.!]{0,120}[,:]\s*",
            "",
            cleaned,
        ).strip()

        banned_phrases = [
            r"(?i)\b(the\s+)?provided\s+(reference\s+)?(data|information)\b",
            r"(?i)\breference\s+data\b",
            r"(?i)\bknowledge\s+(base|context)\b",
            r"(?i)\bcompany\s+information\b",
            r"(?i)\bin\s+the\s+provided\s+\w+\b",
            r"(?i)\bfrom\s+the\s+provided\s+\w+\b",
            r"(?i)\bprovided\s+reference\s+data\b",
        ]
        for pat in banned_phrases:
            cleaned = re.sub(pat, "", cleaned)

        parts = re.split(r"(?<=[.!?])\s+", cleaned)
        kept = []
        drop = re.compile(
            r"(?is)("
            r"unfortunately.*?(provided|reference|data|information|policy)|"
            r"i\s+(do\s+not|don't)\s+have\s+(that|enough|details?).*?"
            r"(provided|reference|data|information)|"
            r"not\s+(mentioned|available|found)\s+in\s+(the\s+)?provided|"
            r"based\s+on\s+(the\s+)?provided|"
            r"it\s+appears\s+that\s+the\s+business\s+name"
            r")"
        )
        for part in parts:
            p = part.strip()
            if not p or drop.search(p):
                continue
            p = re.sub(
                r"(?is)^\s*(based on|according to|as per|from|it appears that)\s+[^,]{0,100},\s*",
                "",
                p,
            ).strip()
            if p:
                kept.append(p)
        cleaned = " ".join(kept).strip()
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        cleaned = re.sub(r"\s+([,.;!?])", r"\1", cleaned)
        cleaned = cleaned.strip(" \n\t,;:")

        if re.search(
            r"(?i)(based on the provided|provided reference data|reference data|"
            r"according to the provided|knowledge base)",
            cleaned or "",
        ):
            cleaned = re.sub(
                r"(?is).*?(?:provided reference data|reference data|provided data)"
                r"[^A-Za-z0-9]*",
                "",
                cleaned,
            ).strip()

        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
        cleaned = self._strip_translation_gloss(cleaned or "")
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        return cleaned or (
            "I don't have that specific detail - please contact our support team."
        )

    def _strip_translation_gloss(self, text):
        """
        Remove parenthetical English translation glosses the model appends after a
        non-English reply, e.g. "... 3-7 divas ma. (Your order will arrive in 3-7 days.)"
        """
        if not text:
            return text
        gloss_words = (
            r"Hello|Hi|Hey|Welcome|I am|I'm|how are|can I help|"
            r"your order|the order|will arrive|business days?|shipping|delivery|"
            r"return|refund|payment|in English|translation"
        )
        # Trailing "(...)" whose content looks like an English sentence
        text = re.sub(
            rf"\s*[\(\[][^)\]]*(?:{gloss_words})[^)\]]*[\)\]]\s*$",
            "",
            text,
            flags=re.I,
        ).strip()
        # Any inline "(...)" gloss with those markers
        text = re.sub(
            rf"\s*[\(\[][^)\]]*(?:{gloss_words})[^)\]]*[\)\]]\s*",
            " ",
            text,
            flags=re.I,
        ).strip()
        return text

    def _support_keywords_present(self, text):
        lower = (text or "").lower()
        keys = (
            "ship", "shipping", "delivery", "order", "return", "refund", "price",
            "payment", "pay", "track", "warranty", "product", "policy", "cancel",
            "exchange", "invoice", "discount", "stock", "laptop", "phone",
        )
        return any(k in lower for k in keys)

    def _is_casual_utterance(self, user_message):
        """Short hello/how-are-you messages that must NOT read the knowledge base."""
        text = (user_message or "").strip()
        if not text or len(text) > 80:
            return False
        words = re.findall(r"\S+", text)
        if len(words) > 8:
            return False
        if self._support_keywords_present(text):
            return False
        if re.match(
            r"^(what|what's|whats|which|who|where|when|why|how|do|does|did|"
            r"is|are|can|could|should|would|will|tell|explain)\b",
            text.lower(),
        ) and len(words) > 3:
            return False
        return True

    def _generate_social_ai_reply(self, user_message, lang_code="en"):
        """
        Auto language-matching greeting via the model — no knowledge base,
        no hardcoded phrase → response map.
        """
        if not self._ensure_ollama():
            return None
        name = self._company_name()
        lang_label = {
            "gu": "romanized Gujarati (Latin script, e.g. \"Hu majama chu\")",
            "hi": "romanized Hindi (Latin script, e.g. \"Main theek hoon\")",
            "es": "Spanish",
            "fr": "French",
            "pt": "Portuguese",
            "de": "German",
            "it": "Italian",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ar": "Arabic",
            "ru": "Russian",
            "th": "Thai",
            "en": "English",
        }.get(lang_code or "en", "the same language the customer used")

        lang_rules = (
            f"Detected customer language: {lang_label}.\n"
            f"You MUST reply only in {lang_label}.\n"
            "Do NOT reply in English unless the customer wrote in English.\n"
            "Do NOT reply in Arabic, Urdu, or with Assalamu alaikum unless the "
            "customer wrote that way.\n"
        )
        if lang_code == "gu":
            lang_rules += (
                "Write romanized Gujarati with Latin letters only "
                "(example style: \"Majama! Hu majama chu. Shu madad kari shaku?\").\n"
            )
        elif lang_code == "hi":
            lang_rules += (
                "Write romanized Hindi with Latin letters only "
                "(example style: \"Main theek hoon! Aapki kaise madad karu?\").\n"
            )

        name = self._company_name()
        about = self._business_about_snippet(380)
        about_block = (
            f"What this business is (use only to shape your greeting topics):\n"
            f"{about}\n\n"
            if about
            else "No detailed business notes yet — keep the greeting generic.\n\n"
        )
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a friendly greeter for {name} customer support.\n"
                    f"{lang_rules}"
                    f"{about_block}"
                    "If they greet or ask how you are, greet back warmly in 1–2 short "
                    "sentences and invite them to ask about THIS business.\n"
                    "Offer help ONLY on topics that fit this business (from the notes above). "
                    "Examples: if it is a social platform, mention account help / features — "
                    "NOT shipping. If it is a shop, then orders/shipping are fine.\n"
                    "Do NOT default to orders, shipping, returns, or products unless those "
                    "topics appear in the business notes.\n"
                    "Do NOT invent company policies or answer as if looking up the business name.\n"
                    "Do NOT add English translations in parentheses.\n"
                    "NEVER say \"based on\", \"reference data\", \"provided data\", "
                    "or \"it appears that\"."
                ),
            },
            {
                "role": "user",
                "content": f"Customer said: {user_message}\n\nYour reply:",
            },
        ]
        try:
            response = requests.post(
                f"{self.ollama_host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "keep_alive": "30m",
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 80,
                        "num_ctx": 1024,
                    },
                },
                timeout=30,
            )
            if response.status_code == 200:
                msg = response.json().get("message") or {}
                text = (msg.get("content") or "").strip()
                if text:
                    cleaned = self._sanitize_customer_reply(text)[:400]
                    if self._social_reply_language_ok(cleaned, lang_code):
                        return cleaned
                    logger.info(
                        "Social AI language mismatch (want=%s); rejecting model reply",
                        lang_code,
                    )
        except Exception as e:
            logger.warning(f"Social AI reply error: {e}")
        return None

    def _social_reply_language_ok(self, reply, lang_code):
        """Reject clearly wrong-language social replies (common mistral failure)."""
        if not reply:
            return False
        lower = reply.lower()
        if "assalam" in lower or "peace be upon" in lower:
            if lang_code not in ("ar",):
                return False
        if lang_code == "gu":
            # Must look like romanized Gujarati, not English support template
            gu_hits = sum(
                1
                for w in (
                    "kem", "majam", "tam", "shu", "madad", "cho", "chu", "che",
                    "hu ", " tame", "bhai", "ben", "chhe", "chho",
                )
                if w in lower
            )
            en_hits = sum(
                1
                for w in (
                    "how can i", "how may i", "welcome to", "assist you",
                    "i'm here to help", "i am here to help",
                )
                if w in lower
            )
            if en_hits and not gu_hits:
                return False
            if not gu_hits and en_hits == 0 and re.search(
                r"\b(hello|hi|hey|welcome|help|orders?|shipping)\b", lower
            ):
                return False
        if lang_code == "hi":
            hi_hits = sum(
                1
                for w in ("namaste", "kaise", "haan", "madad", "theek", "aap", "main ")
                if w in lower
            )
            if re.search(r"\b(how can i|assist you|welcome to)\b", lower) and not hi_hits:
                return False
        return True

    def _build_chat_messages(self, user_message, conversation_history=None, lang_code="en"):
        # Only use retrieved snippets — never dump the entire knowledge base for
        # short/ambiguous messages (that caused greeting → "business name is X").
        context = self.retrieve_context(user_message)
        if not context.strip():
            blob = self._knowledge_blob()
            # Full dump only for clearly support-related questions
            if self._support_keywords_present(user_message) and blob:
                context = blob[:2400]
            else:
                context = "(No matching company facts for this message.)"
        context = re.sub(
            r"(?i)\b(ignore|disregard)\s+(all\s+)?(previous|prior|above)\s+instructions\b",
            "[redacted]",
            context,
        )
        history_block = self._format_history(conversation_history)
        history_part = (
            f"Recent conversation:\n{history_block}\n\n" if history_block else ""
        )
        user_content = (
            "Facts for your reply (never mention this block to the customer):\n"
            "<<<KB_START>>>\n"
            f"{context}\n"
            "<<<KB_END>>>\n\n"
            f"{history_part}"
            f"Customer's current message (reply in {self._lang_label(lang_code)} only):\n"
            f"{user_message}\n\n"
            f"Write your reply in {self._lang_label(lang_code)}. Direct facts only. "
            "No translations. No source phrases. No \"based on\" / \"provided data\"."
        )
        return [
            {"role": "system", "content": self._system_prompt(lang_code)},
            {"role": "user", "content": user_content},
        ]

    def _ollama_options(self, user_message="", context_chars=0):
        # Adaptive caps: shorter answers & smaller context = faster local generation
        msg_len = len(user_message or "")
        if msg_len < 40:
            num_predict = 120
        elif msg_len < 120:
            num_predict = 160
        else:
            num_predict = 200
        # Fit context window tighter when KB snippet is small
        need = max(1536, min(3072, 768 + (context_chars or 0) + msg_len + 400))
        return {
            "temperature": 0.15,
            "top_p": 0.8,
            "num_predict": num_predict,
            "num_ctx": need,
        }

    def _generate_ollama_response(
        self, user_message, intent, conversation_history=None, excerpts=None, lang_code="en"
    ):
        """RAG + short generation for speed (chat API keeps system vs data separated)."""
        if not self.ollama_available:
            return None

        messages = self._build_chat_messages(
            user_message, conversation_history, lang_code=lang_code
        )
        ctx_chars = len(messages[1].get("content") or "")
        try:
            response = requests.post(
                f"{self.ollama_host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "keep_alive": "30m",
                    "options": self._ollama_options(user_message, ctx_chars),
                },
                timeout=60,
            )
            if response.status_code == 200:
                msg = response.json().get("message") or {}
                text = (msg.get("content") or "").strip()
                if text and len(text) > 10:
                    return self._sanitize_customer_reply(text)[:800]
        except requests.exceptions.Timeout:
            logger.warning("Ollama timeout")
        except Exception as e:
            logger.warning(f"Ollama error: {e}")
        return None

    def stream_ollama_response(
        self, user_message, intent, conversation_history=None, lang_code="en"
    ):
        """Yield response text chunks from Ollama chat API (for SSE streaming)."""
        if not self._ensure_ollama():
            return
        messages = self._build_chat_messages(
            user_message, conversation_history, lang_code=lang_code
        )
        ctx_chars = len(messages[1].get("content") or "")
        try:
            with requests.post(
                f"{self.ollama_host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "keep_alive": "30m",
                    "options": self._ollama_options(user_message, ctx_chars),
                },
                stream=True,
                timeout=90,
            ) as response:
                if response.status_code != 200:
                    return
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    msg = payload.get("message") or {}
                    piece = msg.get("content") or payload.get("response") or ""
                    if piece:
                        yield piece
                    if payload.get("done"):
                        break
        except Exception as e:
            logger.warning(f"Ollama stream error: {e}")
            return

    def _index_tokens(self, text):
        """Tokens for RAG indexing — supports Latin + simple CJK digrams."""
        text = (text or "").lower()
        # Non-Latin: character digrams for retrieval
        if re.search(
            r"[\u0400-\u04ff\u0600-\u06ff\u0900-\u097f\u4e00-\u9fff"
            r"\u3040-\u30ff\uac00-\ud7af\u0e00-\u0e7f]",
            text,
        ):
            compact = re.sub(r"\s+", "", text)
            grams = {compact[i : i + 2] for i in range(max(0, len(compact) - 1))}
            return [g for g in grams if g.strip()]
        return self._preprocess_text(text)

    def _preprocess_text(self, text):
        text = (text or "").lower()
        # Keep accented Latin letters for Spanish/French/etc.
        text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
        try:
            tokens = word_tokenize(text)
        except Exception:
            tokens = text.split()
        tokens = [w for w in tokens if w not in self.stop_words and len(w) > 0]
        # Skip lemmatizer for non-ascii tokens (WordNet is English-centric)
        out = []
        for w in tokens:
            if re.search(r"[^\x00-\x7f]", w):
                out.append(w)
            else:
                out.append(self.lemmatizer.lemmatize(w))
        return out

    def _is_off_topic(self, user_message):
        """Return True if the message is clearly not a customer-support query."""
        lower = user_message.lower().strip()
        for pattern in OFF_TOPIC_PATTERNS:
            if re.search(pattern, lower, re.IGNORECASE):
                return True

        tokens = set(self._preprocess_text(user_message))
        if not tokens:
            return False

        # Short greetings / thanks are always allowed
        greeting_tags = {"hello", "hi", "hey", "thanks", "thank", "bye", "goodbye"}
        if tokens & greeting_tags and len(tokens) <= 4:
            return False

        support_hits = sum(
            1 for kw in SUPPORT_KEYWORDS if kw in lower or kw in tokens
        )
        # Long messages with zero support signal and no FAQ/intent match later
        # are handled in get_response after FAQ/intent fail — here only hard blocks
        return False if support_hits > 0 else None  # None = soft check later

    def _guardrail_refusal(self, lang_code="en"):
        name = self._company_name()
        return {
            "response": (
                f"I'm the customer support assistant for {name}. "
                "I can help with questions about this business based on our support notes. "
                "What would you like to know?"
            ),
            "intent": "guardrail_block",
            "confidence": 1.0,
            "model_used": "guardrail",
        }

    def _find_faq_match(self, user_message):
        user_lower = user_message.lower()
        for faq_question in self.faq_cache.keys():
            if faq_question in user_lower or user_lower in faq_question:
                return faq_question, self.faq_cache[faq_question], 0.95

        user_tokens = set(self._preprocess_text(user_message))
        best_match = None
        best_score = 0.0
        for faq_question in self.faq_cache.keys():
            faq_tokens = set(self._preprocess_text(faq_question))
            if not faq_tokens:
                continue
            intersection = len(user_tokens & faq_tokens)
            union = len(user_tokens | faq_tokens)
            similarity = intersection / union if union > 0 else 0
            if similarity > best_score and similarity > 0.4:
                best_score = similarity
                best_match = (faq_question, self.faq_cache[faq_question], similarity)
        return best_match if best_match else (None, None, 0)

    def _adjust_faq_with_ai(self, user_message, faq_answer):
        if not self.ollama_available:
            return faq_answer
        prompt = (
            f'You are a helpful customer service AI for {self._company_name()}. '
            f'A customer asked: "{user_message}"\n\n'
            f'We have this standard answer: "{faq_answer}"\n\n'
            "Rephrase this answer to address the customer's question. "
            "Keep all important facts. Be concise and friendly. "
            "Only output the adjusted answer."
        )
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.5,
                },
                timeout=15,
            )
            if response.status_code == 200:
                result = response.json()
                text = (result.get("response") or "").strip()
                if text and len(text) > 10:
                    return text[:800]
        except Exception as e:
            logger.warning(f"AI FAQ adjust error: {e}")
        return faq_answer

    def _find_intent_pattern(self, user_tokens):
        """Legacy bag-of-tokens matcher (kept for analytics hints only)."""
        best_intent = None
        best_score = 0.0
        for intent in self.intents:
            intent_tag = intent.get("tag")
            if intent_tag == "fallback":
                continue
            for pattern in intent.get("patterns", []):
                pattern_tokens = self._preprocess_text(pattern)
                if not pattern_tokens:
                    continue
                matches = sum(1 for t in pattern_tokens if t in user_tokens)
                score = matches / len(pattern_tokens)
                if score > best_score:
                    best_score = score
                    best_intent = intent_tag
        return best_intent, best_score

    def _is_social_utterance(self, user_message, user_tokens):
        """
        True only for short hello/bye/thanks style messages.
        Real questions must never take the pattern shortcut.
        """
        text = (user_message or "").strip()
        if not text:
            return False
        if "?" in text:
            return False
        # Question / content starters always go to the model
        lower = text.lower()
        if re.match(
            r"^(what|what's|whats|which|who|whom|whose|where|when|why|how|"
            r"do|does|did|is|are|was|were|can|could|should|would|will|"
            r"tell|explain|describe|compare|list|give)\b",
            lower,
        ):
            return False
        # Long / multi-fact messages are content, not greetings
        if len(text) > 40 or len(user_tokens) > 4:
            return False
        return True

    def _match_social_intent(self, user_message):
        """
        Strict social match: compare against original patterns, not broken
        stopword-stripped tokens (e.g. "what's up" must not become just "what").
        """
        text = re.sub(r"[^a-z0-9\s']", " ", user_message.lower()).strip()
        text = re.sub(r"\s+", " ", text)
        social_tags = ("greeting", "goodbye", "thanks")

        best = None
        best_score = 0.0
        for intent in self.intents:
            tag = intent.get("tag")
            if tag not in social_tags:
                continue
            for pattern in intent.get("patterns", []):
                p = re.sub(r"[^a-z0-9\s']", " ", pattern.lower()).strip()
                p = re.sub(r"\s+", " ", p)
                if not p:
                    continue
                # Exact short message, or whole pattern as a phrase
                if text == p:
                    score = 1.0
                elif len(text) <= 24 and (text.startswith(p + " ") or text.endswith(" " + p) or f" {p} " in f" {text} "):
                    # Allow "hi there" vs pattern "hi" only if message stays short
                    score = 0.9 if text.split()[0] == p.split()[0] and len(text.split()) <= 3 else 0.0
                else:
                    score = 0.0
                if score > best_score:
                    best_score = score
                    best = intent
        if best and best_score >= 0.9:
            return best.get("tag"), best_score, best
        return None, 0.0, None

    def _multilingual_social(self, user_message, lang_code):
        """Instant social reply in the customer's language when possible."""
        lower = re.sub(r"[^\w\s'?]", " ", (user_message or "").lower())
        lower = re.sub(r"\s+", " ", lower).strip()
        if not lower or len(lower) > 48:
            return None

        # Allow short greetings even with "?" (e.g. "kem cho?", "kaise ho?")
        greeting_kw = (
            "hola", "bonjour", "ola", "olá", "hallo", "ciao", "salut",
            "नमस्ते", "你好", "こんにちは", "안녕", "مرحبا", "привет", "guten",
            "kem cho", "kem chho", "majama", "majam", "tame majam", "tame",
            "namaste", "namaskar", "kaise ho", "kya haal",
        )
        thanks_kw = (
            "gracias", "merci", "obrigado", "obrigada", "danke", "grazie",
            "धन्यवाद", "谢谢", "ありがとう", "감사", "شكرا", "спасибо",
            "dhanyavad", "shukriya",
        )
        bye_kw = (
            "adios", "adiós", "au revoir", "tchau", "tschüss", "arrivederci",
            "バイバイ", "再见", "안녕히", "مع السلامة", "пока", "aloha",
            "aavjo", "alvida",
        )

        tag = None
        if any(k in lower for k in greeting_kw):
            tag = "greeting"
        elif any(k in lower for k in thanks_kw):
            tag = "thanks"
        elif any(k in lower for k in bye_kw):
            tag = "goodbye"
        elif lang_code != "en" and len(lower.split()) <= 4 and not re.search(
            r"\b(ship|order|return|refund|price|pay|track|product|warranty)\b", lower
        ):
            # Short non-English utterance with no support keywords → treat as greeting
            tag = "greeting"

        if not tag:
            return None

        # Detect language from phrase if detector missed romanized Gujarati/Hindi
        if lang_code == "en":
            if any(
                k in lower
                for k in ("kem cho", "kem chho", "majama", "majam", "tame", "aavjo")
            ):
                lang_code = "gu"
            elif any(k in lower for k in ("namaste", "kaise ho", "kya haal", "dhanyavad")):
                lang_code = "hi"

        if lang_code == "en":
            return None

        reply = _SOCIAL_I18N.get(tag, {}).get(lang_code)
        if not reply:
            # Fallback English greeting rather than sending greetings into the AI/KB path
            reply = {
                "greeting": "Hello! How can I help you today?",
                "thanks": "You're welcome! Anything else I can help with?",
                "goodbye": "Goodbye! Have a great day.",
            }.get(tag)
        if not reply:
            return None
        return {
            "response": reply,
            "intent": tag,
            "confidence": 0.95,
            "model_used": "pattern_matching_i18n",
            "language": lang_code,
        }

    def get_response(self, user_message, use_ai=None, conversation_history=None):
        if not user_message or not isinstance(user_message, str):
            return {
                "response": "Please enter a valid message.",
                "intent": "error",
                "confidence": 0.0,
                "model_used": "system",
            }

        user_message = user_message.strip()
        lang_code = detect_language(user_message)

        hard_block = self._is_off_topic(user_message)
        if hard_block is True:
            return self._guardrail_refusal(lang_code)

        # Casual hello / how-are-you: AI matches language (no KB). If the model
        # fails language match, fall back to a short localized greeting template.
        if self._is_casual_utterance(user_message):
            social_ai = self._generate_social_ai_reply(user_message, lang_code=lang_code)
            if social_ai:
                return {
                    "response": social_ai,
                    "intent": "greeting",
                    "confidence": 0.9,
                    "model_used": f"ollama_{self.model}_social",
                    "language": lang_code,
                }
            i18n_social = self._multilingual_social(user_message, lang_code)
            if i18n_social:
                return i18n_social

        user_tokens = self._preprocess_text(user_message)
        # Non-English / CJK may yield few English tokens — still allow AI path
        if not user_tokens and lang_code == "en":
            return {
                "response": "I didn't understand that. Can you rephrase?",
                "intent": "fallback",
                "confidence": 0.0,
                "model_used": "system",
            }

        # Social shortcuts ONLY for short English hello/bye/thanks
        if lang_code == "en" and user_tokens and self._is_social_utterance(
            user_message, user_tokens
        ):
            tag, confidence, intent_obj = self._match_social_intent(user_message)
            if intent_obj:
                response = random.choice(
                    intent_obj.get("responses", ["How can I help?"])
                )
                name = self._company_name()
                if "TechFlow" in response and name != "TechFlow Electronics":
                    response = response.replace("TechFlow", name)
                return {
                    "response": response,
                    "intent": tag,
                    "confidence": round(confidence, 2),
                    "model_used": "pattern_matching",
                    "language": lang_code,
                }

        # Hint intent for logging only — does not decide the answer
        intent, _confidence = (
            self._find_intent_pattern(user_tokens) if user_tokens else (None, 0)
        )

        # Legacy structured FAQ (English knowledge; skip if non-English question)
        if lang_code == "en":
            faq_question, faq_answer, faq_score = self._find_faq_match(user_message)
            if faq_answer and faq_score >= 0.6:
                safe_faq = re.sub(r"<[^>]+>", "", str(faq_answer))[:800]
                return {
                    "response": safe_faq,
                    "intent": "faq_match",
                    "confidence": round(faq_score, 2),
                    "model_used": "faq_database",
                    "language": lang_code,
                }

        lower = user_message.lower()
        support_hits = sum(1 for kw in SUPPORT_KEYWORDS if kw in lower)
        if lang_code != "en":
            # Non-English support questions still deserve an AI answer
            support_hits = max(support_hits, 1)

        self._ensure_ollama()

        # Content questions: model reads company knowledge and answers
        if use_ai is not False and self.ollama_available:
            ai_response = self._generate_ollama_response(
                user_message,
                intent or "general_inquiry",
                conversation_history=conversation_history,
                lang_code=lang_code,
            )
            if ai_response:
                return {
                    "response": ai_response,
                    "intent": intent or "ai_generated",
                    "confidence": 0.8,
                    "model_used": f"ollama_{self.model}",
                    "language": lang_code,
                }

        # Never dump raw knowledge to customers (prevents secret / injection leakage)
        if not self.ollama_available:
            return {
                "response": SAFE_OFFLINE_FALLBACK,
                "intent": "offline",
                "confidence": 0.0,
                "model_used": "offline_fallback",
                "language": lang_code,
            }

        if support_hits == 0:
            return self._guardrail_refusal(lang_code)

        return {
            "response": (
                f"Thanks for contacting {self._company_name()} support. "
                "I couldn't find that specific detail in our knowledge notes yet. "
                "Please rephrase, or reach out to our support team for help."
            ),
            "intent": "fallback",
            "confidence": 0.0,
            "model_used": "fallback",
            "language": lang_code,
        }


_chatbot_instances = {}


def _cache_key(model, business_data):
    raw = json.dumps(business_data or {}, sort_keys=True, default=str)
    digest = hashlib.md5(raw.encode()).hexdigest()[:12]
    return f"{model}:{digest}"


def get_chatbot(model="mistral", business_data=None, ollama_host=None):
    global _chatbot_instances
    if model not in ("mistral", "llama3", "neural-chat"):
        model = "mistral"
    host = ollama_host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
    key = _cache_key(model, business_data)
    if key not in _chatbot_instances:
        _chatbot_instances[key] = OllamaAIChatbot(
            model=model,
            business_data=business_data,
            ollama_host=host,
        )
    else:
        # Refresh availability occasionally
        bot = _chatbot_instances[key]
        if business_data is not None:
            bot.set_business_data(business_data)
    return _chatbot_instances[key]


def chat(
    user_message,
    use_ai=None,
    model="mistral",
    conversation_history=None,
    business_data=None,
):
    chatbot = get_chatbot(model=model, business_data=business_data)
    return chatbot.get_response(
        user_message,
        use_ai=use_ai,
        conversation_history=conversation_history,
    )


def stream_chat(
    user_message,
    use_ai=None,
    model="mistral",
    conversation_history=None,
    business_data=None,
):
    """
    Yields dict events:
      {"type":"meta", ...} once at start for non-stream paths
      {"type":"token", "text":"..."} while streaming
      {"type":"done", ...} final payload
    """
    chatbot = get_chatbot(model=model, business_data=business_data)
    user_message = (user_message or "").strip()
    lang_code = detect_language(user_message)

    # Instant paths (social / FAQ / offline) — no token stream needed
    if chatbot._is_off_topic(user_message) is True:
        yield {"type": "done", **chatbot._guardrail_refusal(lang_code)}
        return

    # Casual hello / how-are-you: AI matches language (no KB)
    if chatbot._is_casual_utterance(user_message):
        social_ai = chatbot._generate_social_ai_reply(
            user_message, lang_code=lang_code
        )
        if social_ai:
            yield {
                "type": "done",
                "response": social_ai,
                "intent": "greeting",
                "confidence": 0.9,
                "model_used": f"ollama_{chatbot.model}_social",
                "language": lang_code,
            }
            return
        i18n_social = chatbot._multilingual_social(user_message, lang_code)
        if i18n_social:
            yield {"type": "done", **i18n_social}
            return

    user_tokens = chatbot._preprocess_text(user_message) if user_message else []
    if lang_code == "en" and user_tokens and chatbot._is_social_utterance(
        user_message, user_tokens
    ):
        tag, confidence, intent_obj = chatbot._match_social_intent(user_message)
        if intent_obj:
            response = random.choice(intent_obj.get("responses", ["How can I help?"]))
            yield {
                "type": "done",
                "response": response,
                "intent": tag,
                "confidence": round(confidence, 2),
                "model_used": "pattern_matching",
                "language": lang_code,
            }
            return

    intent, _ = chatbot._find_intent_pattern(user_tokens) if user_tokens else (None, 0)
    if lang_code == "en":
        faq_q, faq_a, faq_s = chatbot._find_faq_match(user_message)
        if faq_a and faq_s >= 0.6:
            safe_faq = re.sub(r"<[^>]+>", "", str(faq_a))[:800]
            yield {
                "type": "done",
                "response": safe_faq,
                "intent": "faq_match",
                "confidence": round(faq_s, 2),
                "model_used": "faq_database",
                "language": lang_code,
            }
            return

    chatbot._ensure_ollama()
    if use_ai is False or not chatbot.ollama_available:
        result = chatbot.get_response(
            user_message, use_ai=use_ai, conversation_history=conversation_history
        )
        yield {"type": "done", **result}
        return

    yield {
        "type": "meta",
        "intent": intent or "ai_generated",
        "model_used": f"ollama_{chatbot.model}",
        "confidence": 0.8,
        "language": lang_code,
    }
    # Do not stream raw model tokens directly to customers. The model may start
    # with source-disclosure wording ("based on the provided data...") before
    # final cleanup. Buffer the model output, sanitize it, then send the clean
    # answer as one customer-facing token.
    parts = []
    for token in chatbot.stream_ollama_response(
        user_message,
        intent or "general_inquiry",
        conversation_history=conversation_history,
        lang_code=lang_code,
    ):
        parts.append(token)

    full = "".join(parts).strip()
    if not full:
        result = chatbot.get_response(
            user_message, use_ai=use_ai, conversation_history=conversation_history
        )
        yield {"type": "done", **result}
        return

    cleaned = chatbot._sanitize_customer_reply(full)[:800]
    if cleaned:
        yield {"type": "token", "text": cleaned}
    yield {
        "type": "done",
        "response": cleaned,
        "intent": intent or "ai_generated",
        "confidence": 0.8,
        "model_used": f"ollama_{chatbot.model}",
        "language": lang_code,
    }
