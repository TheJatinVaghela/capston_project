# 🗺️ QUICK REFERENCE MAP - WHERE EVERYTHING IS

## 📍 QUICK LOCATION GUIDE

```
D:\customer-service-chatbot\
│
├─ 📚 FAQ QUESTIONS & BUSINESS DATA
│  └─ backend/business_data.json ⭐ MAIN FILE
│     └─ Contains:
│        ├─ faq_common.faqs[] → 10 pre-defined FAQ questions with answers
│        ├─ business_info → Company name, phone, email, hours
│        ├─ products → Laptops, phones, accessories (with specs, prices)
│        ├─ policies → Shipping, returns, warranty, payment, financing
│        ├─ customer_support → Contact info
│        └─ common_issues → Troubleshooting
│
├─ 🏷️ INTENT PATTERNS (for Tier 2)
│  └─ backend/intents.json
│     └─ Contains:
│        └─ 12 intents with patterns & responses
│           ├─ greeting, goodbye, thanks
│           ├─ order_status, refund, payment_issue
│           ├─ account_recovery, shipping, product_info
│           ├─ complaint, contact_support, fallback
│           └─ Each has patterns (what users say) + responses
│
├─ 💬 CONVERSATION HISTORY
│  └─ backend/chat_logs.json
│     └─ Every message + which model answered it
│        ├─ timestamp
│        ├─ user message
│        ├─ bot response
│        ├─ intent
│        ├─ confidence
│        └─ model_used (faq_database / pattern_matching / ollama_*)
│
├─ 🤖 BACKEND CODE
│  ├─ backend/app.py → Flask API (don't edit unless fixing)
│  ├─ backend/chatbot.py → NLP logic (don't edit unless fixing)
│  │  └─ FIXED: Model switching now works! (lines 348-382)
│  ├─ backend/requirements.txt → Dependencies
│  └─ backend/requirements.txt (UPDATED with requests library)
│
├─ 🌐 FRONTEND CODE
│  ├─ frontend/index.html → Web interface
│  ├─ frontend/style.css → Styling & responsive design
│  └─ frontend/script.js → Sends messages to backend, displays responses
│
└─ 📖 DOCUMENTATION
   ├─ README.md → Original README (updated)
   ├─ README_DETAILED.md ⭐ NEW - Read this! (17KB, complete guide)
   ├─ DATA_GUIDE.md ⭐ NEW - Read this! (16KB, data reference)
   ├─ FIXES_AND_IMPROVEMENTS.md ⭐ NEW - What was fixed
   ├─ GETTING_STARTED.txt → Quick start
   ├─ OLLAMA_SETUP.txt → Ollama installation
   ├─ OLLAMA_UPGRADE_SUMMARY.md → Architecture
   ├─ UPGRADE_COMPLETE.txt → Status overview
   └─ .gitignore → Git ignore rules
```

---

## 🎯 WHAT TO EDIT (For Your Business)

### ✅ EDIT THESE FILES:

**1. `backend/business_data.json` (3.5 KB)**
   - Change company name → business_info → name
   - Add your company phone → business_info → phone
   - Add your products → products section
   - Update your shipping costs → policies → shipping
   - Update return policy → policies → returns
   - Add FAQ questions → faq_common → faqs array
   
   **Example - Add new FAQ:**
   ```json
   {
     "question": "Do you have a loyalty program?",
     "answer": "Yes! Sign up for our rewards program...",
     "category": "loyalty"
   }
   ```
   
   After editing: Restart backend `python app.py` ✅

**2. `backend/intents.json` (Optional - 7.7 KB)**
   - Add new greeting patterns
   - Add new intent types
   - Add custom responses
   
   After editing: Restart backend ✅

### ❌ DON'T EDIT THESE (Code Files):

```
- backend/chatbot.py (NLP logic - unless fixing bugs)
- backend/app.py (Flask API - unless fixing bugs)
- backend/requirements.txt (unless adding new libraries)
- frontend/index.html (unless changing UI)
- frontend/style.css (unless changing design)
- frontend/script.js (unless adding features)
```

---

## 📊 THE 10 PRE-DEFINED FAQ QUESTIONS

**File:** `backend/business_data.json` → `faq_common` → `faqs` array

These 10 questions get **INSTANT answers** (< 0.1 seconds):

| # | Question | Answer Location | Response Time |
|---|----------|-----------------|----------------|
| 1 | "What are your shipping options?" | policies.shipping | ⚡ < 0.1s |
| 2 | "How do I return an item?" | policies.returns | ⚡ < 0.1s |
| 3 | "Do you offer warranties?" | policies.warranty | ⚡ < 0.1s |
| 4 | "Can I track my order?" | faq_common | ⚡ < 0.1s |
| 5 | "What payment methods?" | policies.payment | ⚡ < 0.1s |
| 6 | "Do you ship internationally?" | faq_common | ⚡ < 0.1s |
| 7 | "What's your return policy?" | policies.returns | ⚡ < 0.1s |
| 8 | "Do you have financing?" | policies.financing | ⚡ < 0.1s |
| 9 | "How do I contact support?" | customer_support | ⚡ < 0.1s |
| 10 | "What's warranty coverage?" | policies.warranty | ⚡ < 0.1s |

**How to add more FAQs:**
1. Open: `backend/business_data.json`
2. Find: `"faq_common": { "faqs": [`
3. Add new object before closing `]`
4. Save & restart backend

---

## 🔄 HOW TO UPDATE DATA (Step-by-Step)

### Update Company Name

```
File: backend/business_data.json
Find: "business_info": { "name": "TechFlow Electronics"
Change to: "name": "YOUR COMPANY NAME"
Save & Restart backend
```

### Add a New Product

```
File: backend/business_data.json
Find: "products": { "laptops": { "popular_items": [
Add to array:
  {
    "name": "Your Laptop Name",
    "price": "$999",
    "specs": "Your specs",
    "warranty": "2 years"
  }
Save & Restart backend
Now AI will reference this product when asked!
```

### Add New FAQ Question

```
File: backend/business_data.json
Find: "faq_common": { "faqs": [
Add to array:
  {
    "question": "Your question here?",
    "answer": "Your answer here",
    "category": "category_name"
  }
Save & Restart backend
Now system gives instant answer when asked!
```

### Update Shipping Cost

```
File: backend/business_data.json
Find: "policies": { "shipping": {
Update "standard", "express", "overnight" sections
Save & Restart backend
Now system quotes your actual costs!
```

---

## 🏗️ HOW THE 3-TIER SYSTEM WORKS

```
CUSTOMER ASKS: "Can I return something after 30 days?"

TIER 1 - FAQ CHECK (0.05-0.1 seconds)
  ├─ Open: business_data.json
  ├─ Look in: faq_common.faqs[]
  ├─ Find: {question: "What's your return policy?", ...}
  ├─ Extract: "You have 30 days to return..."
  └─ Return: INSTANT ANSWER ✓

RESPONSE TO CUSTOMER:
  "You have 30 days to return unused items..."
  Badge: 📚 FAQ
```

```
CUSTOMER ASKS: "Hello, can you help me?"

TIER 2 - PATTERN MATCHING (0.1-0.3 seconds)
  ├─ Preprocess: "hello, can, you, help, me"
  ├─ Check: intents.json "greeting" patterns
  ├─ Match: "Hello" matches "greeting" intent ✓
  ├─ Randomly select response from intent
  └─ Return: FAST ANSWER ✓

RESPONSE TO CUSTOMER:
  "Hello! Welcome to TechFlow..."
  Badge: 🔍 Pattern
```

```
CUSTOMER ASKS: "What laptop would you recommend for gaming and video editing?"

TIER 1 & 2 DON'T MATCH
  └─ No FAQ match
  └─ No pattern match

TIER 3 - OLLAMA AI (1-3 seconds)
  ├─ Send question to Ollama AI
  ├─ Include context: business_data.json
  │  ├─ Company info
  │  ├─ Products (ProBook 15X, UltraBook Air M2, etc.)
  │  ├─ Specs (i7, RTX 4070, RAM, SSD)
  │  └─ Prices ($1,299, $899)
  ├─ AI thinks: "Gaming = RTX 4070, Video editing = i7 processor"
  ├─ AI recommends: "ProBook 15X Ultra would be perfect because..."
  └─ Return: INTELLIGENT ANSWER ✓

RESPONSE TO CUSTOMER:
  "The ProBook 15X Ultra would be excellent for your needs..."
  Badge: 🤖 Ollama AI (Mistral)
```

---

## 🔧 MODEL SWITCHING (NOW FIXED!)

**What changed:**

Before: System used Mistral for all queries
Now: Each model works and can switch instantly

**How it works:**

```
Frontend: User clicks dropdown → "Llama2"
  ↓
Request: POST /chat with {model: "llama2", message: "..."}
  ↓
Backend: get_chatbot("llama2") 
  ├─ Checks: Is llama2 instance already created?
  ├─ If NO: Creates new OllamaAIChatbot(model="llama2")
  ├─ If YES: Reuses existing instance (cached, fast)
  └─ Returns: llama2 instance
  ↓
Ollama: Sends request to Ollama on port 11434
  ├─ Model: llama2
  ├─ Prompt: business_data + question
  └─ Response: AI-generated answer
  ↓
Frontend: Shows response with badge 🤖 Ollama AI (llama2)
```

**Models:**
- Mistral (4.1GB) - Fastest ⚡⚡⚡
- Llama2 (3.8GB) - Most accurate ⭐⭐⭐⭐
- Neural-Chat (3.8GB) - Best conversation 💬💬💬

---

## 📈 HOW SYSTEM COMBINES ANSWERS

**Example Question:** "I want to return something AND I'm in Canada. What are my options?"

**System Process:**

```
Parse Question:
  ├─ Extract: "return", "Canada", "options"
  └─ Understand: Asking about MULTIPLE topics

TIER 1 - FAQ CHECK:
  ├─ Search FAQ #2: "How do I return an item?"
  │  └─ Match confidence: 90% ✓
  ├─ Search FAQ #6: "Do you ship internationally?"
  │  └─ Match confidence: 85% ✓
  ├─ Found 2 matching FAQs
  └─ Extract both answers

Combine Answers:
  1. "RETURNS: You have 30 days..."
  2. "SHIPPING TO CANADA: Yes, we ship to Canada..."
  
Format Response:
  "Great questions! Here's what you need:
  
  ✓ RETURNS: You have 30 days to return...
  
  ✓ SHIPPING: Yes, we ship to Canada...
  
  Total time to get new item: 2-3 weeks
  
  Need help with anything else?"

Return to Customer:
  Badge: 📚 FAQ (combined 2 FAQs)
  Response time: 0.1 seconds ⚡
```

**Code:** Method `_find_faq_match()` uses Jaccard similarity
**Threshold:** 0.4 (40% token overlap)
**Result:** Fast, contextual, multi-topic responses

---

## 📚 DOCUMENTATION READING ORDER

```
1️⃣ START HERE: README_DETAILED.md (17KB)
   └─ Understand full system, 3-tier architecture
   
2️⃣ THEN: DATA_GUIDE.md (16KB)
   └─ Understand data files, where FAQs are, how to update
   
3️⃣ IF FIXING: FIXES_AND_IMPROVEMENTS.md (11KB)
   └─ Model switching bug fix, what changed
   
4️⃣ QUICK REF: This file (QUICK_REFERENCE.md)
   └─ Quick lookups, where everything is
   
5️⃣ SETUP: OLLAMA_SETUP.txt (15KB)
   └─ Installing Ollama and models
   
6️⃣ ARCHITECTURE: OLLAMA_UPGRADE_SUMMARY.md (14KB)
   └─ Deep dive into design decisions
```

---

## ✅ VERIFICATION CHECKLIST

Before demo, verify:

- [ ] Ollama running: `ollama serve` in Terminal 1
- [ ] Backend running: `python app.py` in Terminal 2
- [ ] Frontend opens: `index.html` in browser
- [ ] Model selector shows 3 options: Mistral, Llama2, Neural-Chat
- [ ] FAQ question returns instant answer (< 0.2s)
- [ ] Pattern question returns fast answer (< 0.5s)
- [ ] AI question returns intelligent answer (1-3s)
- [ ] Model badges display correctly
- [ ] Can switch models and get different responses
- [ ] Chat logs save to `backend/chat_logs.json`
- [ ] Clear button works
- [ ] API endpoints work (/logs, /models, /business-info)

---

## 🚀 QUICK DEMO SCRIPT

```
1. INTRO (10 seconds)
   "This chatbot uses 3-tier system for speed and intelligence"

2. TIER 1 DEMO (5 seconds)
   Q: "What's your shipping cost?"
   A: "Standard (Free over $100), Express ($24.99), Overnight ($49.99)"
   Badge: 📚 FAQ
   "Instant answer from FAQ database"

3. TIER 2 DEMO (5 seconds)
   Q: "Hello, thank you for your help"
   A: "You're welcome! How else can I help?"
   Badge: 🔍 Pattern
   "Fast intent recognition with NLTK"

4. TIER 3 DEMO (10 seconds)
   Q: "Which laptop is best for gaming?"
   A: "ProBook 15X Ultra would be perfect... RTX 4070... $1,299..."
   Badge: 🤖 Ollama AI (Mistral)
   "Intelligent reasoning with business context"

5. MODEL SWITCHING (5 seconds)
   Switch to: Llama2
   Q: "What's your return policy?"
   A: "30 days from purchase..."
   Badge: 📚 FAQ (same question, different model)
   "Now using Llama2 model"

6. CODE QUALITY (3 minutes)
   Show: backend/chatbot.py
   Highlight: Comments, class structure, error handling
   Explain: Why modular design matters

7. CUSTOMIZATION (2 minutes)
   Show: business_data.json
   Explain: "Any company can update this JSON file"
   Demo: Change company name, restart, show updated data

TOTAL: ~15 minutes
```

---

## 📞 EMERGENCY REFERENCE

**Q: Where are FAQ questions?**
A: `backend/business_data.json` → `faq_common` → `faqs` array (10 questions)

**Q: How do I add FAQ?**
A: Edit JSON, add to `faqs` array, restart backend

**Q: Where's business data?**
A: `backend/business_data.json` (products, policies, company info)

**Q: How do I update company info?**
A: Edit `business_data.json` → `business_info` section

**Q: Model switching not working?**
A: Restart backend: Ctrl+C, then `python app.py`

**Q: Ollama not responding?**
A: Check `ollama serve` running in separate terminal

**Q: How does system combine answers?**
A: Matches multiple FAQs, extracts answers, formats together

**Q: Where are logs?**
A: `backend/chat_logs.json` (all messages + model used)

**Q: How to test?**
A: Ask: "What's shipping?" (FAQ), "Hello" (Pattern), "Best laptop?" (AI)

---

## 🎯 KEY FILES SUMMARY

| File | Size | Edit? | Purpose |
|------|------|-------|---------|
| `business_data.json` | 3.5KB | ✅ YES | FAQ, products, policies |
| `intents.json` | 7.7KB | 🟡 Maybe | Intent patterns |
| `chat_logs.json` | Grows | ❌ No | Conversation history |
| `chatbot.py` | 10.5KB | ❌ No | NLP engine |
| `app.py` | 7.5KB | ❌ No | Flask API |
| `requirements.txt` | <1KB | ❌ No | Python packages |
| `index.html` | 1.7KB | ❌ No | Frontend UI |
| `style.css` | 5.2KB | ❌ No | Frontend styling |
| `script.js` | 5.2KB | ❌ No | Frontend logic |

---

**This is your map! Bookmark it for quick reference!** 🗺️

Last Updated: June 6, 2026
