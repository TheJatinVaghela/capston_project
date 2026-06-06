# AI Customer Service Chatbot - Sample Test Questions

This document contains 35+ sample test questions organized by intent. Use these questions to test the chatbot''s ability to recognize intents and generate appropriate responses.

## Greeting Intent
Expected: "Hello! Welcome to our customer service. How can I help you today?"
- Hello
- Hi there
- Hey, I need help
- Good morning
- Greetings
- What''s up
- Hey

## Goodbye Intent  
Expected: "Goodbye! Thank you for using our service. Have a great day!"
- Goodbye
- Bye bye
- See you later
- Farewell
- Take care
- That''s all for now
- See you soon

## Thanks Intent
Expected: "You''re welcome! Is there anything else I can help you with?"
- Thank you
- Thanks a lot
- I appreciate your help
- Thanks so much
- Thank you very much
- Much appreciated
- You''ve been very helpful

## Order Status Intent
Expected: "To check your order status, please provide your order ID..."
- Where is my order
- Track my package
- What''s the status of my order
- When will my order arrive
- How long does delivery take
- Track my order please
- Where is my package
- When will I receive my order
- Can you tell me about my delivery

## Refund Intent
Expected: "We offer refunds within 30 days of purchase..."
- I want a refund
- How do I return something
- Can I get my money back
- I want to return my order
- What''s your refund policy
- How can I cancel my order
- I need to return this item
- Do you offer refunds

## Payment Issue Intent
Expected: "I''m sorry you''re experiencing payment issues..."
- My payment failed
- Transaction was declined
- My card isn''t working
- I have a billing problem
- I was charged twice
- Payment error occurred
- I can''t complete checkout
- My credit card was rejected

## Account Recovery Intent
Expected: "You can reset your password by clicking ''Forgot Password''..."
- I forgot my password
- How do I reset my password
- I can''t log into my account
- I forgot my username
- My account is locked
- I''m locked out
- How do I access my account
- I need to recover my account

## Shipping Intent
Expected: "Shipping costs depend on your location..."
- How much does shipping cost
- Do you have free shipping
- What shipping options are available
- How long does shipping take
- Do you ship internationally
- Express shipping available
- What are the delivery options
- Can I change my shipping address

## Product Info Intent
Expected: "We offer a wide range of products..."
- What products do you sell
- Tell me about your products
- Do you have this item in stock
- Can you recommend a product
- What''s your best-selling product
- Is this available
- Do you carry this brand
- What sizes do you have

## Complaint Intent
Expected: "I''m sorry to hear about your experience..."
- I want to file a complaint
- Your service is terrible
- I had a bad experience
- I''m not satisfied with my purchase
- The product is defective
- I received a damaged item
- Poor quality product
- I''m very disappointed

## Contact Support Intent
Expected: "You can reach our support team via email..."
- How do I contact support
- Can I speak to someone
- I need to talk to a human
- What''s your phone number
- How do I reach customer service
- Where''s your support email
- Do you have live chat
- What''s your support number

## Loyalty Program Intent
Expected: "Join our loyalty program and earn points..."
- Do you have a rewards program
- How do I earn loyalty points
- What are membership benefits
- Do you have VIP programs
- How do I get discount codes
- What''s your rewards system
- Can I earn points on purchases

## Fallback/Unknown Intent
Expected: "I''m not sure I understand. Could you please rephrase that..."
- Xyzabc qwerty
- 12345
- Random gibberish text
- sdfjkl;
- This doesn''t match any pattern
- Lorem ipsum dolor
- !@#$%^&*()

---

## Testing Tips

1. **Test Each Intent**: Go through each intent group and try at least 2-3 variations
2. **Check Confidence Scores**: Look at the confidence percentage shown under bot responses
3. **Typos & Variations**: Try with typos or different word orders to test robustness
4. **Multiple Messages**: Send several messages in succession to test conversation flow
5. **Check Intent Recognition**: Verify the displayed intent tag matches the test category
6. **Response Diversity**: Send same intent multiple times to see if bot varies responses
7. **Performance**: Note response times - should be immediate (< 1 second)
8. **Logging**: Check that messages appear in /logs endpoint

## Expected Behavior

- ✅ Bot should recognize most variations within each intent category
- ✅ Confidence scores should be visible (0-100%)
- ✅ Random responses within an intent should vary
- ✅ Fallback should trigger only when no good match found
- ✅ Chat messages should be logged to chat_logs.json
- ✅ Clear Chat button should reset the conversation
- ✅ Enter key should send message (no need to click Send)

