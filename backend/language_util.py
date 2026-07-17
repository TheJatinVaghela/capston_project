"""Lightweight language detection (no external model dependency)."""

from __future__ import annotations

import re
from typing import Optional

# Script ranges for non-Latin languages
_SCRIPT_RANGES = [
    ("zh", re.compile(r"[\u4e00-\u9fff]")),
    ("ja", re.compile(r"[\u3040-\u30ff]")),
    ("ko", re.compile(r"[\uac00-\ud7af]")),
    ("ar", re.compile(r"[\u0600-\u06ff]")),
    ("hi", re.compile(r"[\u0900-\u097f]")),  # also covers Gujarati-adjacent Devanagari
    ("gu", re.compile(r"[\u0a80-\u0aff]")),  # Gujarati script
    ("ru", re.compile(r"[\u0400-\u04ff]")),
    ("th", re.compile(r"[\u0e00-\u0e7f]")),
]

# Marker words for common Latin-script / romanized languages
_MARKERS = {
    "es": (
        "hola", "gracias", "por favor", "envio", "envío", "devolver", "devolucion",
        "devolución", "precio", "pedido", "ayuda", "buenos", "buenas", "quiero",
        "necesito", "política", "politica", "reembolso",
    ),
    "fr": (
        "bonjour", "merci", "livraison", "retour", "remboursement",
        "commande", "aide", "prix", "s'il", "svp", "salut",
    ),
    "pt": (
        "olá", "ola", "obrigado", "obrigada", "envio", "devolver", "pedido",
        "ajuda", "preço", "preco", "reembolso",
    ),
    "de": (
        "hallo", "guten", "danke", "lieferung", "rückgabe", "ruckgabe",
        "bestellung", "hilfe", "preis", "rückerstattung",
    ),
    "it": (
        "ciao", "grazie", "salve", "spedizione", "reso", "ordine", "aiuto",
        "prezzo", "rimborso",
    ),
    # Romanized Gujarati / Hindi greetings & common words
    "gu": (
        "kem cho", "kem cho?", "kem chho", "kem chho?", "majama", "majama?",
        "majam", "tame majama", "tame majam", "tame", "su chale", "su chale?",
        "aavjo", "aavjo ne", "dhanyavad", "madad", "kem", "bhai", "ben",
    ),
    "hi": (
        "namaste", "namaskar", "kaise ho", "kaise ho?", "kya haal", "shukriya",
        "dhanyavad", "madad", "kaise", "haan", "nahi",
    ),
}

_LANG_NAMES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "pt": "Portuguese",
    "de": "German",
    "it": "Italian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "gu": "Gujarati",
    "ru": "Russian",
    "th": "Thai",
}


def language_name(code: str) -> str:
    return _LANG_NAMES.get(code or "en", "English")


def detect_language(text: str) -> str:
    """
    Fast heuristic language id. Defaults to English.
    Good enough to steer the model; not a full NLU detector.
    """
    raw = (text or "").strip()
    if not raw:
        return "en"

    for code, pattern in _SCRIPT_RANGES:
        if pattern.search(raw):
            return code

    lower = raw.lower().strip()
    folded = (
        lower.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ñ", "n")
        .replace("ü", "u")
    )

    # Exact / phrase markers first (romanized Indian greetings etc.)
    for code in ("gu", "hi", "es", "fr", "pt", "de", "it"):
        for phrase in _MARKERS.get(code, ()):
            if phrase in folded or folded.rstrip("?!.,") == phrase.rstrip("?!.,"):
                return code

    tokens = set(re.findall(r"[a-zA-ZÀ-ÿ']+", folded))
    if not tokens and re.search(r"[¿¡]", raw):
        return "es"

    scores = {}
    for code, words in _MARKERS.items():
        scores[code] = sum(1 for w in words if w in folded or w in tokens)

    if scores:
        best = max(scores, key=scores.get)
        if scores[best] >= 1:
            if "¿" in raw or "¡" in raw:
                return "es"
            return best

    return "en"


def reply_language_instruction(code: Optional[str]) -> str:
    name = language_name(code or "en")
    if (code or "en") == "en":
        return "Reply in English unless the customer clearly uses another language."
    return (
        f"The customer is writing in {name}. Reply entirely in {name}. "
        "If facts are in English, translate them naturally into the customer's language. "
        "Never mention internal sources, policies files, or company documents by name."
    )
