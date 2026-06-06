"""
Flask API Backend - Upgraded with Ollama AI Support
Hybrid Q&A System with Pattern Matching + AI Generation
"""

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
from datetime import datetime, timezone

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os
from chatbot import chat

app = Flask(__name__)
CORS(app)
def now_utc():
    return datetime.now(timezone.utc).isoformat()
# In-memory conversation history
conversation_history = []
CHAT_LOGS_FILE = 'chat_logs.json'

# Current AI model
current_model = 'mistral'


def _ensure_logs_file():
    """Ensure chat_logs.json exists."""
    if not os.path.exists(CHAT_LOGS_FILE):
        with open(CHAT_LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)


def _load_logs():
    """Load chat logs from file."""
    _ensure_logs_file()
    try:
        with open(CHAT_LOGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []


def _save_logs(logs):
    """Save chat logs to file."""
    try:
        with open(CHAT_LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving logs: {e}")


@app.route('/', methods=['GET'])
def home():
    """Health check endpoint."""
    return jsonify({
        "status": "running",
        "message": "AI Customer Service Chatbot with Ollama Integration",
        "version": "2.0.0",
        "features": [
            "Pattern-based FAQ matching",
            "NLTK NLP preprocessing",
            "Ollama AI integration (Mistral, Llama2, Neural-Chat)",
            "Hybrid Q&A system",
            "Business knowledge base"
        ]
    }), 200


@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """
    Main chat endpoint with Ollama support.
    
    Request JSON:
    {
        "message": "user message here",
        "use_ai": false,  # Optional: force AI or pattern matching
        "model": "mistral"  # Optional: choose model
    }
    """
    try:
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({
                "error": "Missing or invalid JSON body",
                "response": "Send valid JSON with Content-Type: application/json",
                "intent": "error",
                "confidence": 0.0,
                "model_used": "system",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }), 400
        if not isinstance(data, dict):
            logger.error(f"Invalid JSON format: {data}")
            return jsonify({"error": "Invalid JSON format"}), 400
        logger.info(f"Received chat request: {data}")

        if not data or 'message' not in data:
            return jsonify({
                "error": "Invalid request. 'message' field required.",
                "response": "Please provide a message.",
                "intent": "error",
                "confidence": 0.0,
                "model_used": "system",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }), 400
        
        logger.info(f"Processing message: {data['message']}")
        user_message = data.get('message', '').strip()
        use_ai = data.get('use_ai', None)  # None = auto-decide
        model = data.get('model', 'mistral')
        
        if not user_message:
            return jsonify({
                "error": "Message cannot be empty.",
                "response": "Please enter a message.",
                "intent": "error",
                "confidence": 0.0,
                "model_used": "system",
                "timestamp": now_utc()
            }), 400
        logger.info(f"User message: {user_message}, use_ai: {use_ai}, model: {model}")
        # Get response from chatbot (with model selection)
        chatbot_response = chat(user_message, use_ai=use_ai, model=model)

        # FORCE normalization (VERY IMPORTANT)
        if not isinstance(chatbot_response, dict):
            chatbot_response = {
                "response": str(chatbot_response),
                "intent": "system",
                "confidence": 1.0,
                "model_used": "fallback"
            }
        
        chatbot_response['timestamp'] = now_utc()
        chatbot_response['user_message'] = user_message
        
        # Store in memory
        conversation_history.append({
            "user": user_message,
            "bot": chatbot_response['response'],
            "intent": chatbot_response['intent'],
            "confidence": chatbot_response['confidence'],
            "model_used": chatbot_response['model_used'],
            "timestamp": chatbot_response['timestamp']
        })
        
        # Save to file
        try:
            logs = _load_logs()
            logs.append({
                "user": user_message,
                "bot": chatbot_response['response'],
                "intent": chatbot_response['intent'],
                "confidence": chatbot_response['confidence'],
                "model_used": chatbot_response['model_used'],
                "timestamp": chatbot_response['timestamp']
            })
            _save_logs(logs)
        except Exception as e:
            print(f"Warning: Could not save log: {e}")
        
        return jsonify(chatbot_response), 200
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            "error": str(e),
            "response": "An error occurred processing your request.",
            "intent": "error",
            "confidence": 0.0,
            "model_used": "system",
            "timestamp": now_utc()
        }), 500


@app.route('/models', methods=['GET'])
def get_models():
    """List available Ollama models."""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        
        if response.status_code == 200:
            models = [tag['name'] for tag in response.json().get('models', [])]
            return jsonify({
                "ollama_available": True,
                "available_models": models,
                "recommended": "mistral, llama2, neural-chat"
            }), 200
        else:
            return jsonify({
                "ollama_available": False,
                "message": "Ollama not responding",
                "solution": "Start Ollama with: ollama serve"
            }), 200
    
    except Exception as e:
        return jsonify({
            "ollama_available": False,
            "message": str(e),
            "solution": "Install and start Ollama from: https://ollama.ai"
        }), 200


@app.route('/logs', methods=['GET'])
def get_logs():
    """Retrieve all chat logs."""
    try:
        logs = _load_logs()
        return jsonify({
            "total": len(logs),
            "logs": logs
        }), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "total": 0,
            "logs": []
        }), 500


@app.route('/logs', methods=['DELETE'])
def clear_logs():
    """Clear all chat logs."""
    try:
        _save_logs([])
        global conversation_history
        conversation_history = []
        
        return jsonify({
            "status": "success",
            "message": "All chat logs cleared."
        }), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "failed"
        }), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get chatbot statistics."""
    try:
        logs = _load_logs()
        
        intent_counts = {}
        model_usage = {}
        
        for log in logs:
            intent = log.get('intent', 'unknown')
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            
            model = log.get('model_used', 'unknown')
            model_usage[model] = model_usage.get(model, 0) + 1
        
        confidences = [log.get('confidence', 0) for log in logs if log.get('confidence', 0) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return jsonify({
            "total_messages": len(logs),
            "average_confidence": round(avg_confidence, 2),
            "intent_distribution": intent_counts,
            "model_usage": model_usage
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/business-info', methods=['GET'])
def get_business_info():
    """Get business information."""
    try:
        with open('business_data.json', 'r') as f:
            data = json.load(f)
            return jsonify(data.get('business_info', {})), 200
    except:
        return jsonify({"error": "Business info not available"}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "GET /",
            "POST /chat",
            "GET /models",
            "GET /logs",
            "DELETE /logs",
            "GET /stats",
            "GET /business-info"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500


if __name__ == '__main__':
    _ensure_logs_file()
    
    print("=" * 70)
    print("AI Customer Service Chatbot with Ollama Integration")
    print("=" * 70)
    print("Server: http://127.0.0.1:5000")
    print("Frontend: ../frontend/index.html")
    print("")
    print("Features:")
    print("  ✓ Pattern-based FAQ matching")
    print("  ✓ NLTK NLP preprocessing")
    print("  ✓ Ollama AI integration")
    print("  ✓ Business knowledge base (TechFlow Electronics)")
    print("  ✓ Hybrid Q&A system")
    print("")
    print("Make sure Ollama is running:")
    print("  ollama serve")
    print("")
    print("Pull models if needed:")
    print("  ollama pull mistral")
    print("  ollama pull llama2")
    print("  ollama pull neural-chat")
    print("=" * 70)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
