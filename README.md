# AI-Powered Customer Service Chatbot

A capstone-grade customer service chatbot using Python, Flask, NLTK, Ollama, React, and SQLite.

## Project Overview

Hybrid Q&A system for TechFlow Electronics:

```
User Input → FAQ Match → Pattern Matching → Ollama AI → Response
```

## Features

- 12 intent categories with NLTK pattern matching
- 26 FAQ entries in business knowledge base
- Ollama AI integration (Mistral, Llama2, Neural-Chat)
- React + MUI frontend with mobile-responsive layout
- SQLite database for session logging and analytics
- Multi-turn conversation context for Ollama responses

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.7+, Flask 2.3.3 |
| NLP | NLTK 3.8.1 |
| AI | Ollama (local) |
| Frontend | React 18, Vite, MUI 5 |
| Database | SQLite |
| API | REST (JSON) |

## Project Structure

```
customer-service-chatbot/
├── backend/
│   ├── app.py              # Flask API server
│   ├── chatbot.py          # NLTK + Ollama engine
│   ├── database.py         # SQLite logging layer
│   ├── intents.json        # 12 intent categories
│   ├── business_data.json  # Company info, products, FAQs
│   ├── requirements.txt
│   └── run_tests.py        # Intent test runner
├── frontend-react/         # React + MUI chat UI (primary)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api/chatApi.js
│   │   ├── components/
│   │   └── theme/
│   └── package.json
├── frontend/               # Legacy HTML/JS UI (fallback)
├── docs/
│   ├── sample_test_questions.md
│   └── test_results.md
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.7+
- Node.js 18+ (for React frontend)
- Ollama (optional, for AI responses)

### 1. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Backend runs at `http://127.0.0.1:5000`. SQLite database (`chat_logs.db`) is created automatically.

### 2. Ollama (optional)

```bash
ollama serve
ollama pull mistral
```

FAQ and pattern matching work without Ollama.

### 3. React Frontend

```bash
cd frontend-react
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### 4. Legacy Frontend (fallback)

Open `frontend/index.html` directly in a browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/chat` | Send message (`message`, `model`, `use_ai`, `session_id`) |
| GET | `/models` | List Ollama models |
| GET | `/logs` | Chat logs (`?session_id=`) |
| DELETE | `/logs` | Clear all logs |
| GET | `/sessions/<id>/messages` | Session message history |
| GET | `/stats` | Intent/model analytics |
| GET | `/business-info` | Company information |

## Testing

```bash
cd backend
python run_tests.py
```

See [docs/test_results.md](docs/test_results.md) for full results (87% pass rate, 31 tests).

## Customization

Edit `backend/business_data.json` to update:
- Company info (`business_info`)
- Products (`products`)
- Policies (`policies`)
- FAQs (`faq_common.faqs`)

Edit `backend/intents.json` to add intent patterns.

Restart the backend after changes.

## Team

Dev Pankajkumar Bajaniya | Jatin Vaghela | Pratikkumar Bhupendrabhai Chavda | Amal Satheesan | Karop Dezosa Sebastian

Lambton College — AML-2404 AI and ML Lab
