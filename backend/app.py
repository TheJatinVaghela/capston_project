"""
Flask API Backend - Upgraded with Ollama AI Support
Hybrid Q&A System with Pattern Matching + AI Generation
"""

import logging
import uuid

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
from datetime import datetime, timezone

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from chatbot import chat
import database as db

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5000", "http://127.0.0.1:5000"])


def now_utc():
    return datetime.now(timezone.utc).isoformat()


@app.route('/', methods=['GET'])
def home():
    """Health check endpoint."""
    return jsonify({
        "status": "running",
        "message": "AI Customer Service Chatbot with Ollama Integration",
        "version": "3.0.0",
        "features": [
            "Pattern-based FAQ matching",
            "NLTK NLP preprocessing",
            "Ollama AI integration (Mistral, Llama2, Neural-Chat)",
            "Hybrid Q&A system",
            "Business knowledge base",
            "SQLite session logging",
            "React frontend support"
        ]
    }), 200


@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """
    Main chat endpoint with Ollama support.

    Request JSON:
    {
        "message": "user message here",
        "use_ai": false,
        "model": "mistral",
        "session_id": "optional-uuid"
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
                "timestamp": now_utc()
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
                "timestamp": now_utc()
            }), 400

        user_message = data.get('message', '').strip()
        use_ai = data.get('use_ai', None)
        model = data.get('model', 'mistral')
        session_id = data.get('session_id') or str(uuid.uuid4())

        if not user_message:
            return jsonify({
                "error": "Message cannot be empty.",
                "response": "Please enter a message.",
                "intent": "error",
                "confidence": 0.0,
                "model_used": "system",
                "timestamp": now_utc(),
                "session_id": session_id
            }), 400

        logger.info(f"User message: {user_message}, use_ai: {use_ai}, model: {model}, session: {session_id}")

        conversation_history = db.get_recent_conversation(session_id, limit=6)

        chatbot_response = chat(
            user_message,
            use_ai=use_ai,
            model=model,
            conversation_history=conversation_history,
        )

        if not isinstance(chatbot_response, dict):
            chatbot_response = {
                "response": str(chatbot_response),
                "intent": "system",
                "confidence": 1.0,
                "model_used": "fallback"
            }

        timestamp = now_utc()
        chatbot_response['timestamp'] = timestamp
        chatbot_response['user_message'] = user_message
        chatbot_response['session_id'] = session_id

        try:
            db.save_message(session_id, 'user', user_message, timestamp=timestamp)
            db.save_message(
                session_id, 'bot', chatbot_response['response'],
                intent=chatbot_response['intent'],
                confidence=chatbot_response['confidence'],
                model_used=chatbot_response['model_used'],
                timestamp=timestamp,
            )
        except Exception as e:
            logger.warning(f"Could not save to database: {e}")

        return jsonify(chatbot_response), 200

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
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
    """Retrieve chat logs."""
    try:
        session_id = request.args.get('session_id')
        limit = request.args.get('limit', 100, type=int)
        logs = db.get_logs(session_id=session_id, limit=limit)
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
        db.clear_logs()
        return jsonify({
            "status": "success",
            "message": "All chat logs cleared."
        }), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "failed"
        }), 500


@app.route('/sessions/<session_id>/messages', methods=['GET'])
def get_session_messages(session_id):
    """Return all messages for a session (for page refresh / history load)."""
    try:
        messages = db.get_session_messages(session_id)
        return jsonify({
            "session_id": session_id,
            "total": len(messages),
            "messages": messages
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get chatbot statistics from SQLite."""
    try:
        return jsonify(db.get_stats()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/business-info', methods=['GET'])
def get_business_info():
    """Get business information."""
    try:
        with open('business_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return jsonify(data.get('business_info', {})), 200
    except Exception:
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
            "GET /sessions/<session_id>/messages",
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
    db.init_db()

    print("=" * 70)
    print("AI Customer Service Chatbot with Ollama Integration")
    print("=" * 70)
    print("Server: http://127.0.0.1:5000")
    print("React Frontend: ../frontend-react (npm run dev -> http://localhost:5173)")
    print("Legacy Frontend: ../frontend/index.html")
    print("")
    print("Features:")
    print("  Pattern-based FAQ matching")
    print("  NLTK NLP preprocessing")
    print("  Ollama AI integration")
    print("  SQLite session logging")
    print("  React + MUI frontend support")
    print("")
    print("Make sure Ollama is running:")
    print("  ollama serve")
    print("=" * 70)

    app.run(debug=True, host='127.0.0.1', port=5000)
