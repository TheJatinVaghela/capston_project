const API_URL = "http://127.0.0.1:5000";
const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const clearBtn = document.getElementById("clearBtn");
const modelSelect = document.getElementById("modelSelect");
const aiModeToggle = document.getElementById("aiModeToggle");
const aiModeStatus = document.getElementById("aiModeStatus");

let currentModel = "mistral";
let aiModeEnabled = true;

// Initialize chat with welcome message
function initializeChat() {
    const welcomeMsg = {
        text: "👋 Welcome to TechFlow Electronics Support! I''m powered by Ollama AI (Mistral/Llama2). I can help with:\n\n✓ Product information (laptops, phones, accessories)\n✓ Shipping & delivery questions\n✓ Returns & refunds\n✓ Payment & account issues\n✓ Warranty information\n✓ Loyalty programs\n\nAsk me anything about our products or services!",
        isBot: true,
        intent: "greeting",
        confidence: 1.0,
        model_used: "system"
    };
    displayMessage(welcomeMsg);
}

// Display message in chat box
function displayMessage(msg) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${msg.isBot ? "bot" : "user"}`;
    
    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";
    contentDiv.textContent = msg.text;
    msgDiv.appendChild(contentDiv);
    
    if (msg.isBot) {
        const metaDiv = document.createElement("div");
        metaDiv.className = "message-meta";
        
        // Intent badge
        if (msg.intent && msg.intent !== "fallback") {
            const intentBadge = document.createElement("span");
            intentBadge.className = "badge intent-badge";
            intentBadge.textContent = msg.intent;
            metaDiv.appendChild(intentBadge);
        }
        
        // Confidence badge
        if (msg.confidence !== undefined && msg.confidence > 0) {
            const confBadge = document.createElement("span");
            confBadge.className = "badge confidence-badge";
            confBadge.textContent = `${(msg.confidence * 100).toFixed(0)}%`;
            metaDiv.appendChild(confBadge);
        }
        
        // Model badge
        if (msg.model_used) {
            const modelBadge = document.createElement("span");
            let badgeClass = "badge model-badge";
            
            if (msg.model_used === "faq_database") {
                badgeClass = "badge faq-badge";
                modelBadge.textContent = "📚 FAQ";
            } else if (msg.model_used.includes("ollama")) {
                badgeClass = "badge ai-badge";
                modelBadge.textContent = "🤖 Ollama AI";
            } else if (msg.model_used === "pattern_matching") {
                badgeClass = "badge model-badge";
                modelBadge.textContent = "🔍 Pattern";
            } else {
                modelBadge.textContent = msg.model_used;
            }
            
            modelBadge.className = badgeClass;
            metaDiv.appendChild(modelBadge);
        }
        
        msgDiv.appendChild(metaDiv);
    }
    
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "message bot";
    typingDiv.id = "typingIndicator";
    
    const indicatorDiv = document.createElement("div");
    indicatorDiv.className = "typing-indicator";
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement("div");
        dot.className = "typing-dot";
        indicatorDiv.appendChild(dot);
    }
    
    typingDiv.appendChild(indicatorDiv);
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById("typingIndicator");
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Send message to backend
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Display user message
    displayMessage({
        text: message,
        isBot: false
    });
    
    // Clear input
    userInput.value = "";
    userInput.focus();
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ 
                message: message,
                use_ai: aiModeEnabled ? null : false,  // null = auto, false = FAQ only
                model: currentModel
            })
        });
        
        removeTypingIndicator();
        console.log( response);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        displayMessage({
            text: data.response,
            isBot: true,
            intent: data.intent,
            confidence: data.confidence,
            model_used: data.model_used
        });
        
    } catch (error) {
        removeTypingIndicator();
        console.error("Error:", error);
        displayMessage({
            text: "❌ Connection error. Make sure backend is running at http://127.0.0.1:5000\n\nAlso check: is Ollama running? (ollama serve)",
            isBot: true,
            intent: "error",
            confidence: 0,
            model_used: "system"
        });
    }
}

// Clear chat
function clearChat() {
    chatBox.innerHTML = "";
    initializeChat();
    userInput.value = "";
    userInput.focus();
}

// Update AI mode display
function updateAIModeStatus() {
    aiModeStatus.textContent = aiModeEnabled ? "Auto (FAQ + AI)" : "FAQ Only";
}

// Event listeners
sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});
clearBtn.addEventListener("click", clearChat);

modelSelect.addEventListener("change", (e) => {
    currentModel = e.target.value;
    displayMessage({
        text: `✓ Switched to ${currentModel} model`,
        isBot: true,
        intent: "system",
        confidence: 1.0,
        model_used: "system"
    });
});

aiModeToggle.addEventListener("change", (e) => {
    aiModeEnabled = e.target.checked;
    updateAIModeStatus();
    displayMessage({
        text: aiModeEnabled ? "✓ AI mode enabled (FAQ + AI)" : "✓ FAQ-only mode enabled",
        isBot: true,
        intent: "system",
        confidence: 1.0,
        model_used: "system"
    });
});

// Initialize on page load
window.addEventListener("load", () => {
    initializeChat();
    updateAIModeStatus();
    userInput.focus();
});
