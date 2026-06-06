"""
Upgraded Chatbot with Ollama AI Integration
Hybrid system: Common FAQs + AI-powered responses for complex queries
"""

import json
import random
import re
import requests
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)
# NLTK imports (kept for preprocessing)
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
        
except ImportError:
    print("WARNING: NLTK not installed")


class OllamaAIChatbot:
    """
    Advanced chatbot with Ollama AI integration.
    
    System: Hybrid Q&A
    1. Common FAQs → Fast template response
    2. Unusual queries → Ollama AI generation
    """
    
    def __init__(self, intents_file='intents.json', business_file='business_data.json', 
                 ollama_host='http://localhost:11434', model='mistral'):
        """
        Initialize chatbot with Ollama support.
        
        Args:
            intents_file: Path to intents JSON
            business_file: Path to business knowledge base
            ollama_host: Ollama API endpoint
            model: 'mistral' or 'llama2' or 'neural-chat'
        """
        self.intents_file = intents_file
        self.business_file = business_file
        self.ollama_host = ollama_host
        self.model = model
        
        # Load data
        self.intents = self._load_intents()
        self.business_data = self._load_business_data()
        self.faq_cache = self._build_faq_cache()
        
        # NLTK setup
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Check Ollama availability
        self.ollama_available = self._check_ollama()
        
    def _load_intents(self):
        """Load intents from JSON file."""
        try:
            with open(self.intents_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('intents', [])
        except FileNotFoundError:
            print(f"Error: {self.intents_file} not found!")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.intents_file}!")
            return []
    
    def _load_business_data(self):
        """Load business knowledge base."""
        try:
            with open(self.business_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.business_file} not found!")
            return {}
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {self.business_file}!")
            return {}
    
    def _build_faq_cache(self):
        """Build quick lookup for common FAQs."""
        faq_cache = {}
        faq_common = self.business_data.get('faq_common', [])
        if isinstance(faq_common, dict):
            faqs = faq_common.get('faqs', [])
        elif isinstance(faq_common, list):
            faqs = faq_common
        else:
            faqs = []

        for faq in faqs:
            if not isinstance(faq, dict):
                continue
            question = faq.get('question', '').lower()
            faq_cache[question] = faq.get('answer', '')
        return faq_cache
    
    def _check_ollama(self):
        try:
            response = requests.get(f'{self.ollama_host}/api/tags', timeout=2)

            if response.status_code == 200:
                data = response.json()

                models = []
                for tag in data.get('models', []):
                    # SAFE handling for both dict and string formats
                    if isinstance(tag, dict):
                        name = tag.get('name', '')
                    else:
                        name = str(tag)

                    models.append(name.split(':')[0])

                available = any(self.model in m for m in models)

                if available:
                    print(f"✓ Ollama connected! Model '{self.model}' available.")
                    return True
                else:
                    print(f"⚠ Model '{self.model}' not found.")
                    return False

        except requests.exceptions.ConnectionError:
            print("⚠ Ollama not running. Start with: ollama serve")
            return False
        except Exception as e:
            print(f"⚠ Ollama check failed: {e}")
            return False
    
    def _preprocess_text(self, text):
        """Preprocess text (same as before)."""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word not in self.stop_words and len(word) > 0]
        tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        return tokens
    
    def _find_faq_match(self, user_message):
        """
        Try to match user query with FAQ database.
        Returns (matched_question, answer, similarity_score) or (None, None, 0)
        """
        user_lower = user_message.lower()
        
        # Direct substring match (fast)
        for faq_question in self.faq_cache.keys():
            if faq_question in user_lower or user_lower in faq_question:
                return faq_question, self.faq_cache[faq_question], 0.95
        
        # Token-based similarity
        user_tokens = set(self._preprocess_text(user_message))
        
        best_match = None
        best_score = 0.0
        
        for faq_question in self.faq_cache.keys():
            faq_tokens = set(self._preprocess_text(faq_question))
            
            if len(faq_tokens) == 0:
                continue
            
            # Calculate Jaccard similarity
            intersection = len(user_tokens & faq_tokens)
            union = len(user_tokens | faq_tokens)
            similarity = intersection / union if union > 0 else 0
            
            if similarity > best_score and similarity > 0.4:
                best_score = similarity
                best_match = (faq_question, self.faq_cache[faq_question], similarity)
        
        if best_match:
            return best_match
        return (None, None, 0)
    
    def _adjust_faq_with_ai(self, user_message, faq_answer):
        """
        Use AI to adjust/rephrase FAQ answer to match user's specific question.
        Makes answer more relevant to user's exact phrasing.
        
        Args:
            user_message: User's specific question
            faq_answer: Pre-written FAQ answer
        
        Returns:
            Adjusted answer from AI or original if AI fails
        """
        if not self.ollama_available:
            return faq_answer
        
        # Build prompt to rephrase FAQ answer based on user's question
        adjustment_prompt = f"""You are a helpful customer service AI. A customer asked: "{user_message}"

We have this standard answer: "{faq_answer}"

Please rephrase this answer to directly address the customer's specific question while keeping all the important information. Be concise and friendly. Just provide the adjusted answer, nothing else."""
        
        try:
            response = requests.post(
                f'{self.ollama_host}/api/generate',
                json={
                    'model': self.model,
                    'prompt': adjustment_prompt,
                    'stream': False,
                    'temperature': 0.5,  # Lower temp for consistency
                    'top_p': 0.9,
                    'top_k': 40
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()

                if isinstance(result, dict):
                    adjusted_text = result.get('response') or result.get('message') or ''
                else:
                    adjusted_text = str(result)

                adjusted_text = adjusted_text.strip()
                if adjusted_text and len(adjusted_text) > 10:
                    return adjusted_text[:500]  # Limit to 500 chars
        
        except Exception as e:
            print(f"AI adjustment error: {e}")
        
        return faq_answer  # Return original if AI fails
    
    def _generate_ollama_response(self, user_message, intent, context=""):
        """
        Generate AI response using Ollama for complex queries.
        
        Args:
            user_message: Original user query
            intent: Recognized intent
            context: Business context to include
        """
        if not self.ollama_available:
            return None
        
        # Build context for Ollama
        business_context = f"""
You are a helpful customer service AI for {self.business_data.get('business_info', {}).get('name', 'our business')}.

Business Info:
{json.dumps(self.business_data.get('business_info', {}), indent=2)}

Policies:
{json.dumps(self.business_data.get('policies', {}), indent=2)}

Customer Query: {user_message}
Recognized Intent: {intent}

Provide a helpful, professional response. Be concise (1-2 sentences). Stay in character as a customer service agent.
"""
        
        try:
            response = requests.post(
                f'{self.ollama_host}/api/generate',
                json={
                    'model': self.model,
                    'prompt': business_context,
                    'stream': False,
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'top_k': 40
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()

                if isinstance(result, dict):
                    generated_text = result.get('response') or result.get('message') or ''
                else:
                    generated_text = str(result)

                generated_text = generated_text.strip()
                
                # Clean up the response
                if generated_text:
                    return generated_text[:500]  # Limit to 500 chars
            
        except requests.exceptions.Timeout:
            print("Ollama timeout - response taking too long")
        except Exception as e:
            print(f"Ollama error: {e}")
        
        return None
    
    def _find_intent_pattern(self, user_tokens):
        """Find matching intent using pattern matching (original logic)."""
        best_intent = None
        best_score = 0.0
        
        for intent in self.intents:
            intent_tag = intent.get('tag')
            patterns = intent.get('patterns', [])
            
            if intent_tag == 'fallback':
                continue
            
            for pattern in patterns:
                pattern_tokens = self._preprocess_text(pattern)
                
                if len(pattern_tokens) == 0:
                    continue
                
                matches = sum(1 for token in pattern_tokens if token in user_tokens)
                score = matches / len(pattern_tokens) if len(pattern_tokens) > 0 else 0
                
                if score > best_score:
                    best_score = score
                    best_intent = intent_tag
        
        return best_intent, best_score
    
    def get_response(self, user_message, use_ai=None):
        """
        Main response function - Hybrid approach.
        
        Args:
            user_message: User query
            use_ai: Force AI mode (None = auto-decide)
        
        Returns:
            dict with response, intent, confidence, model_used
        """
        if not user_message or not isinstance(user_message, str):
            return {
                "response": "Please enter a valid message.",
                "intent": "error",
                "confidence": 0.0,
                "model_used": "system"
            }
        
        user_message = user_message.strip()
        user_tokens = self._preprocess_text(user_message)
        
        if not user_tokens:
            return {
                "response": "I didn't understand that. Can you rephrase?",
                "intent": "fallback",
                "confidence": 0.0,
                "model_used": "system"
            }
        
        # STEP 1: Try FAQ match (fastest, but adjust with AI if available)
        faq_question, faq_answer, faq_score = self._find_faq_match(user_message)
        
        if faq_answer:
            # If Ollama available and not FAQ-only mode, adjust answer with AI
            if self.ollama_available and use_ai is not False:
                adjusted_answer = self._adjust_faq_with_ai(user_message, faq_answer)
                return {
                    "response": adjusted_answer,
                    "intent": "faq_match",
                    "confidence": round(faq_score, 2),
                    "model_used": f"faq_database_adjusted_by_{self.model}"
                }
            else:
                # Return original FAQ answer if AI not available or FAQ-only mode
                return {
                    "response": faq_answer,
                    "intent": "faq_match",
                    "confidence": round(faq_score, 2),
                    "model_used": "faq_database"
                }
        
        # STEP 2: Try pattern matching
        intent, confidence = self._find_intent_pattern(user_tokens)
        
        if intent and confidence >= 0.3:
            # Found a pattern match
            for intent_obj in self.intents:
                if intent_obj.get('tag') == intent:
                    response = random.choice(intent_obj.get('responses', ['How can I help?']))
                    return {
                        "response": response,
                        "intent": intent,
                        "confidence": round(confidence, 2),
                        "model_used": "pattern_matching"
                    }
        
        # STEP 3: Use Ollama AI for unusual queries (if available)
        if use_ai or (self.ollama_available and not use_ai is False):
            ai_response = self._generate_ollama_response(
                user_message, 
                intent or "general_inquiry"
            )
            
            if ai_response:
                return {
                    "response": ai_response,
                    "intent": intent or "ai_generated",
                    "confidence": 0.8,
                    "model_used": f"ollama_{self.model}"
                }
        
        # STEP 4: Fallback
        for intent_obj in self.intents:
            if intent_obj.get('tag') == 'fallback':
                response = random.choice(intent_obj.get('responses', ['I could not understand that.']))
                return {
                    "response": response,
                    "intent": "fallback",
                    "confidence": 0.0,
                    "model_used": "fallback"
                }
        
        return {
            "response": "I apologize, I couldn't process your request. Please contact support.",
            "intent": "error",
            "confidence": 0.0,
            "model_used": "system"
        }


# Global instances (one per model to avoid reloading)
_chatbot_instances = {}


def get_chatbot(model='mistral'):
    """
    Get or create chatbot instance for specific model.
    Each model gets its own instance (cached).
    """
    global _chatbot_instances
    
    # Validate model
    if model not in ['mistral', 'llama2', 'neural-chat']:
        model = 'mistral'
    logger.info(f"Requesting chatbot instance for model: {model}")
    # Create new instance if doesn't exist for this model
    if model not in _chatbot_instances:
        _chatbot_instances[model] = OllamaAIChatbot(model=model)
    logger.info(f"Chatbot instance for model '{model}' is ready.")
    return _chatbot_instances[model]


def chat(user_message, use_ai=None, model='mistral'):
    """
    Get response from chatbot with model selection.
    
    Args:
        user_message: User query
        use_ai: Force AI/FAQ mode (None = auto)
        model: 'mistral', 'llama2', or 'neural-chat'
    
    Returns:
        dict with response, intent, confidence, model_used
    """
    logger.info(f"Chat called with model: {model}, use_ai: {use_ai}")
    chatbot = get_chatbot(model)
    logger.info(f"Chatbot instance for model '{model}' ready. Processing message...")
    return chatbot.get_response(user_message, use_ai=use_ai)
