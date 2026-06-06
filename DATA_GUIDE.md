# 📊 DATA GUIDE - Where Everything Is & How to Update

Complete guide to all data files, FAQ questions, business information, and how the system uses them.

---

## 🎯 QUICK OVERVIEW - HOW SYSTEM WORKS

```
User Question
    ↓
┌─────────────────────────────────────────┐
│ TIER 1: FAQ Database (0.1 seconds) ⚡   │ ← business_data.json
│ Fast instant answers for common Qs      │
└─────────────────────────────────────────┘
    ↓ (if no FAQ match)
┌─────────────────────────────────────────┐
│ TIER 2: Pattern Matching (0.2 seconds) 🔍│ ← intents.json
│ Intent recognition (greeting, goodbye,  │
│ order_status, refund, etc.)             │
└─────────────────────────────────────────┘
    ↓ (if no pattern match)
┌─────────────────────────────────────────┐
│ TIER 3: Ollama AI (1-3 seconds) 🤖      │ ← business_data.json
│ Smart reasoning for unique questions    │ (used as context)
└─────────────────────────────────────────┘
    ↓
Answer to User
```

---

## 📁 FILES THAT STORE DATA

### 1️⃣ **business_data.json** (MAIN DATABASE) 
**Location:** `backend/business_data.json`

**Size:** ~3.5 KB

**Purpose:** Complete knowledge base about your business, products, policies, and FAQ

**How it's used:**
- ✅ Tier 1: FAQ matching (fast lookup)
- ✅ Tier 3: Context injection for AI (so Ollama knows about your products)
- ✅ API endpoint: `/business-info` returns this data to frontend

**What it contains:**

```json
{
  "business_info": {
    "name": "TechFlow Electronics",
    "phone": "1-800-TECHFLOW",
    "email": "support@techflowelectronics.com",
    ...more company details
  },
  
  "products": {
    "laptops": {
      "category": "Laptops & Computers",
      "popular_items": [
        {
          "name": "ProBook 15X Ultra",
          "price": "$1,299",
          "specs": "Intel i7, 16GB RAM, 512GB SSD, RTX 4070",
          "warranty": "2 years"
        }
        ...more products
      ]
    },
    "smartphones": {...},
    "accessories": {...}
  },
  
  "policies": {
    "shipping": {
      "standard": { "time": "5-7 business days", "cost": "Free over $100" },
      "express": { "time": "2-3 business days", "cost": "$24.99" },
      "overnight": { "time": "Next day", "cost": "$49.99" }
    },
    "returns": {...},
    "warranty": {...},
    "payment": {...},
    "financing": {...}
  },
  
  "faq_common": {
    "faqs": [
      {
        "question": "What are your shipping options?",
        "answer": "We offer Standard (Free over $100)...",
        "category": "shipping"
      },
      {
        "question": "How do I return an item?",
        "answer": "You have 30 days to return...",
        "category": "returns"
      },
      ...10 more FAQs
    ]
  },
  
  "customer_support": {...},
  "common_issues": {...}
}
```

---

### 2️⃣ **intents.json** (INTENT PATTERNS)
**Location:** `backend/intents.json`

**Size:** ~7.7 KB

**Purpose:** Intent patterns for Tier 2 (Pattern Matching)

**How it's used:**
- ✅ Pattern matching engine (NLTK preprocessing)
- ✅ Intent recognition (greeting, goodbye, thanks, etc.)
- ✅ Generates responses for recognized intents

**What it contains:**

```json
{
  "intents": [
    {
      "tag": "greeting",
      "patterns": [
        "Hello",
        "Hi there",
        "Hey",
        "Good morning",
        "Good evening",
        "Greetings"
      ],
      "responses": [
        "Hello! Welcome to TechFlow Electronics...",
        "Hi there! How can I assist you today?",
        "Greetings! What can I help you with?"
      ]
    },
    
    {
      "tag": "order_status",
      "patterns": [
        "Where is my order?",
        "Track my package",
        "When will I receive my item?",
        "Has my order shipped?",
        "Order tracking",
        "Check order status"
      ],
      "responses": [
        "To track your order, please provide your order number...",
        "You can check your order status in your account...",
        "Visit our tracking page: www.techflowelectronics.com/track"
      ]
    },
    
    ...12 more intents
  ]
}
```

---

### 3️⃣ **chat_logs.json** (CONVERSATION HISTORY)
**Location:** `backend/chat_logs.json`

**Size:** Grows as conversations happen

**Purpose:** Store all customer conversations for analysis

**How it's used:**
- ✅ API endpoint: `GET /logs` returns this
- ✅ API endpoint: `DELETE /logs` clears this
- ✅ Track which model was used for each message
- ✅ Analyze which intents customers ask about

**Structure:**
```json
[
  {
    "timestamp": "2026-06-06T10:13:10.678Z",
    "user": "What's your shipping cost?",
    "bot_response": "We offer Standard (Free over $100)...",
    "intent": "faq_match",
    "confidence": 0.95,
    "model_used": "faq_database"
  },
  {
    "timestamp": "2026-06-06T10:15:22.456Z",
    "user": "Which laptop is best for gaming?",
    "bot_response": "For gaming, I'd recommend the ProBook 15X Ultra...",
    "intent": "ai_generated",
    "confidence": 0.8,
    "model_used": "ollama_mistral"
  }
  ...more messages
]
```

---

## 🔍 PRE-DEFINED FAQ QUESTIONS (WHERE TIER 1 GETS ANSWERS)

These are instant answers - system doesn't need to think!

**Location:** `backend/business_data.json` → `faq_common` → `faqs` array

**Current FAQ Questions (10 total):**

1. **"What are your shipping options?"**
   - Answer: "We offer Standard (Free on orders over $100)..."
   - Response time: 0.05 seconds

2. **"How do I return an item?"**
   - Answer: "You have 30 days to return unused items..."
   - Response time: 0.05 seconds

3. **"Do you offer warranties?"**
   - Answer: "Yes! All products come with manufacturer warranty..."
   - Response time: 0.05 seconds

4. **"Can I track my order?"**
   - Answer: "Yes! You can track your order via the link..."
   - Response time: 0.05 seconds

5. **"What payment methods do you accept?"**
   - Answer: "We accept all major credit cards, PayPal..."
   - Response time: 0.05 seconds

6. **"Do you offer international shipping?"**
   - Answer: "Currently we ship to USA and Canada..."
   - Response time: 0.05 seconds

7. **"What's your return policy?"**
   - Answer: "30 days from purchase, item must be unused..."
   - Response time: 0.05 seconds

8. **"Do you have financing options?"**
   - Answer: "Yes! We offer 0% APR for 12 months on orders over $500..."
   - Response time: 0.05 seconds

9. **"How do I contact customer support?"**
   - Answer: "Call 1-800-TECHFLOW or email support@..."
   - Response time: 0.05 seconds

10. **"What's your warranty coverage?"**
    - Answer: "Standard 1-2 year manufacturer warranty..."
    - Response time: 0.05 seconds

---

## 🤖 HOW SYSTEM COMBINES ANSWERS FOR COMPLEX QUESTIONS

**Example: Customer asks "Can I return something after 2 weeks? And what about shipping to Canada?"**

### System Process:

```
STEP 1: Parse Question
  → "return" + "2 weeks"
  → "shipping" + "Canada"

STEP 2: Check FAQ for matches
  → FAQ: "How do I return an item?" → MATCH (95% confidence)
  → FAQ: "Do you offer international shipping?" → MATCH (95% confidence)

STEP 3: Combine Answers (if multiple FAQs match)
  → Extract both FAQ answers
  → Format together
  → Return combined response

Result to customer:
  "Great question! I can help with both:
  
  ✓ RETURNS: You have 30 days to return items...
  
  ✓ SHIPPING TO CANADA: Yes, we ship to Canada...
  
  Any other questions?"
```

---

## 📝 HOW TO UPDATE BUSINESS DATA

### **EASIEST METHOD: Edit JSON File Directly**

**File:** `backend/business_data.json`

**Steps:**

1. **Open the file:**
   - Right-click `backend/business_data.json`
   - Select "Open with" → VS Code

2. **Find the section you want to update:**

   **To update company info:**
   ```json
   "business_info": {
     "name": "YOUR COMPANY NAME",
     "phone": "YOUR PHONE",
     "email": "YOUR EMAIL",
     ...
   }
   ```

   **To add/update products:**
   ```json
   "products": {
     "laptops": {
       "popular_items": [
         {
           "name": "New Product Name",
           "price": "$999",
           "specs": "Your product specs",
           "warranty": "2 years"
         }
       ]
     }
   }
   ```

   **To update policies:**
   ```json
   "policies": {
     "shipping": {
       "standard": {
         "time": "5-7 business days",
         "cost": "YOUR COST"
       }
     }
   }
   ```

   **To add FAQ questions:**
   ```json
   "faq_common": {
     "faqs": [
       {
         "question": "Your new question here?",
         "answer": "Your answer here",
         "category": "shipping" or "returns" or "warranty" or "other"
       }
     ]
   }
   ```

3. **Save the file** (Ctrl+S)

4. **Restart backend:**
   ```bash
   # Stop: Press Ctrl+C in terminal
   # Then restart:
   python app.py
   ```

5. **Test:** Ask your chatbot the new question!

---

## 🎯 IMPORTANT: FAQ vs PATTERN vs AI

### **FAQ (Tier 1) - Use For:**
- ✅ Common questions (shipping, returns, warranty, payment)
- ✅ Questions that have exact fixed answers
- ✅ Fastest responses needed
- ✅ Most customer queries (80%)

**Example:** "What are your shipping costs?"

### **PATTERN MATCHING (Tier 2) - Use For:**
- ✅ Greetings ("Hello", "Hi", "Good morning")
- ✅ Closings ("Goodbye", "Thank you", "Thanks")
- ✅ Standard intents (complaint, order_status, refund)
- ✅ When question structure matches known pattern

**Example:** "I want to return my order"

### **OLLAMA AI (Tier 3) - Use For:**
- ✅ Unique/complex questions
- ✅ Questions combining multiple topics
- ✅ Product recommendations
- ✅ Questions not in FAQ or patterns
- ✅ When customer mentions specific scenarios

**Example:** "Which laptop would you recommend for gaming and video editing?"

---

## 📊 RESPONSE TIME BREAKDOWN

| Tier | Type | Time | Best For |
|------|------|------|----------|
| 1 | FAQ Lookup | 0.05-0.1s ⚡ | Common questions |
| 2 | Pattern Matching | 0.1-0.3s 🔍 | Intents, greetings |
| 3 | Ollama AI | 1-3s 🤖 | Complex, unique |

---

## 🔧 HOW TO ADD NEW FAQ QUESTIONS

**Current FAQs:** 10  
**You can add more!**

**Steps:**

1. Open: `backend/business_data.json`

2. Find: `"faq_common": { "faqs": [`

3. Add new question before the closing `]`:
   ```json
   {
     "question": "Can you match competitor prices?",
     "answer": "We're committed to offering competitive pricing. If you find a lower price, contact our support team at 1-800-TECHFLOW and we'll be happy to discuss options.",
     "category": "pricing"
   }
   ```

4. Save file

5. Restart backend

6. Test by asking: "Can you match competitor prices?"

---

## 📈 TRACKING WHICH MODEL ANSWERS WHAT

**Every response includes `model_used` field:**

```json
{
  "response": "...",
  "intent": "...",
  "confidence": 0.95,
  "model_used": "faq_database"     ← This shows which tier!
}
```

**Model Used Values:**
- `faq_database` = Tier 1 (fastest)
- `pattern_matching` = Tier 2 (medium)
- `ollama_mistral` = Tier 3 (AI - Mistral model)
- `ollama_llama2` = Tier 3 (AI - Llama2 model)
- `ollama_neural-chat` = Tier 3 (AI - Neural-Chat model)
- `fallback` = No match, generic response

**Check logs:** `backend/chat_logs.json`

---

## 🎓 EXAMPLE: COMBINING MULTIPLE FAQ ANSWERS

**Scenario:** Customer asks "I want to return my laptop but ship it overnight to another state. What's the fastest way?"

**System does:**

1. **Parse question:**
   - Return → refund concept
   - Overnight shipping → express/overnight concept
   - Different state → shipping question

2. **FAQ checks:**
   - ✓ Found FAQ: "How do I return an item?"
   - ✓ Found FAQ: "What are your shipping options?"
   - ✓ Found policy: shipping costs

3. **Combine response:**
   ```
   "Great question! Here's how to do both:
   
   STEP 1 - RETURN PROCESS:
   You have 30 days to return your laptop. The item must be unused 
   and in original packaging. Return shipping is free!
   
   STEP 2 - OVERNIGHT SHIPPING:
   Once we receive your return, we can ship a replacement via 
   overnight shipping for $49.99 (next business day delivery).
   
   TOTAL TIME: ~2-3 days (1 day for us to receive + 1 day overnight)
   
   To start: Log into your account and initiate the return."
   ```

4. **Response badge shows:** 📚 FAQ (because matched FAQ database)

---

## 🚀 OPTIMIZATION TIPS

### **To Make System Faster (Tier 1 FAQ):**
- Add more common questions to FAQ list
- Keep FAQ answers concise (100-200 words)
- Group related questions

### **To Make System Smarter (Tier 3 AI):**
- Update business_data.json with detailed product specs
- Add real policies and features
- Include troubleshooting in common_issues section

### **To Make System More Accurate:**
- Review chat_logs.json to see failed questions
- Add those questions to FAQ if they're common
- Update intents.json with new patterns if needed

---

## 📚 FILE HIERARCHY SUMMARY

```
customer-service-chatbot/
├── backend/
│   ├── business_data.json ⭐ MAIN DATABASE
│   │   ├── business_info (company details)
│   │   ├── products (catalog)
│   │   ├── policies (shipping, returns, warranty, etc.)
│   │   ├── faq_common ⭐ FAQ QUESTIONS & ANSWERS
│   │   ├── customer_support (contact info)
│   │   └── common_issues (troubleshooting)
│   │
│   ├── intents.json ⭐ INTENT PATTERNS
│   │   └── 12 intent tags with patterns & responses
│   │
│   ├── chat_logs.json ⭐ CONVERSATION HISTORY
│   │   └── Every message + model_used
│   │
│   ├── chatbot.py (NLP engine - DON'T EDIT unless fixing code)
│   ├── app.py (Flask API - DON'T EDIT unless fixing code)
│   └── requirements.txt (Python packages - DON'T EDIT unless adding libs)
│
├── frontend/
│   ├── index.html (UI)
│   ├── style.css (styling)
│   └── script.js (connects to backend)
└── docs/ (documentation)
```

---

## ❓ COMMON QUESTIONS

**Q: Where do I see what FAQ questions are available?**
A: Open `backend/business_data.json` → Find `"faq_common"` section → See `"faqs"` array (10 questions)

**Q: How do I add a new FAQ answer?**
A: Edit `backend/business_data.json` → `faq_common` → `faqs` array → Add new object with question/answer

**Q: How do I update company phone number?**
A: Edit `backend/business_data.json` → `business_info` → Change `"phone"` value → Restart backend

**Q: How do I add a new product?**
A: Edit `backend/business_data.json` → `products` → Choose category (laptops/smartphones/accessories) → Add to `popular_items` array

**Q: Where are customer messages stored?**
A: `backend/chat_logs.json` (one file with all messages + model used)

**Q: Can I see which model answered each question?**
A: Yes! Open `backend/chat_logs.json` → Each message has `"model_used"` field

**Q: How do I reset all chat history?**
A: Delete `backend/chat_logs.json` (will be recreated empty) or use API: `DELETE /logs`

**Q: Can I combine FAQ answers?**
A: Yes! System automatically does this if multiple FAQs match the question

**Q: What if my question isn't in FAQ or patterns?**
A: System uses Ollama AI (Tier 3) + business_data context to generate intelligent answer

---

## 🎯 NEXT STEPS

1. **Review your data:** Open `backend/business_data.json` and understand the structure
2. **Add your company info:** Update business_info section
3. **Add your products:** Update products section with YOUR items
4. **Update policies:** Add your actual shipping/return/warranty policies
5. **Add your FAQs:** Update `faq_common` with questions your real customers ask
6. **Restart backend:** `python app.py`
7. **Test:** Ask your chatbot questions and see which tier answers!

---

**Last Updated:** June 6, 2026
**Version:** 2.0 (Ollama AI Upgrade)
