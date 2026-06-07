"""Quick intent test runner for Week 4 test results."""
import database as db
from chatbot import chat

db.init_db()

TESTS = [
    ("Hello", "greeting"),
    ("Hi there", "greeting"),
    ("Good morning", "greeting"),
    ("Goodbye", "goodbye"),
    ("See you later", "goodbye"),
    ("Thank you", "thanks"),
    ("Thanks a lot", "thanks"),
    ("Where is my order", "order_status"),
    ("Track my package", "order_status"),
    ("I want a refund", "refund"),
    ("How do I return something", "refund"),
    ("My payment failed", "payment_issue"),
    ("Transaction was declined", "payment_issue"),
    ("I forgot my password", "account_recovery"),
    ("I can't log into my account", "account_recovery"),
    ("How much does shipping cost", "shipping"),
    ("Do you ship internationally", "shipping"),
    ("What products do you sell", "product_info"),
    ("Tell me about your products", "product_info"),
    ("I want to file a complaint", "complaint"),
    ("I had a bad experience", "complaint"),
    ("How do I contact support", "contact_support"),
    ("Can I speak to someone", "contact_support"),
    ("Do you have a rewards program", "loyalty_program"),
    ("How do I earn loyalty points", "loyalty_program"),
    ("", "error"),
    ("Xyzabc qwerty", "fallback"),
    ("12345", "fallback"),
]

FAQ_TESTS = [
    ("What are your shipping options?", "faq_match"),
    ("Do you offer free shipping?", "faq_match"),
    ("What laptops do you sell?", "faq_match"),
]

passed = 0
results = []

for msg, expected in TESTS + FAQ_TESTS:
    r = chat(msg, use_ai=False, model="mistral")
    actual = r.get("intent", "unknown")
    ok = actual == expected
    if expected == "fallback" and actual in ("fallback", "error"):
        ok = True
    if ok:
        passed += 1
    status = "PASS" if ok else "FAIL"
    results.append((msg, expected, actual, status, r.get("confidence", 0)))
    print(f"{status}: {msg!r:45s} expected={expected:18s} got={actual}")

total = len(TESTS) + len(FAQ_TESTS)
print(f"\nPassed {passed}/{total}")
