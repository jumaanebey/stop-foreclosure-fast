// AI Assistant Functions - Standalone file
console.log('AI Functions JavaScript loading...');

function openAIAssistant() {
    console.log('AI Assistant button clicked');
    const modal = document.getElementById('ai-assistant-modal');
    console.log('Modal element found:', modal);
    
    if (modal) {
        modal.style.display = 'flex';
        // Check if startChatbot exists before calling it
        if (typeof startChatbot === 'function') {
            startChatbot();
        } else {
            console.log('startChatbot function not yet loaded');
        }
        console.log('Modal opened');
    } else {
        console.error('AI Assistant modal not found!');
        alert('AI Assistant modal not found. Please refresh the page.');
        return;
    }
    
    // Track AI assistant opening
    if (typeof gtag !== 'undefined') {
        gtag('event', 'ai_chatbot_opened', {
            'event_category': 'AI Interaction',
            'event_label': 'Chatbot Started'
        });
    }
}

function closeAIAssistant() {
    console.log('Closing AI Assistant modal');
    const modal = document.getElementById('ai-assistant-modal');
    if (modal) {
        modal.style.display = 'none';
        console.log('Modal hidden');
    }
}

// Make functions globally available immediately
window.openAIAssistant = openAIAssistant;
window.closeAIAssistant = closeAIAssistant;

console.log('AI functions defined and assigned to window');
console.log('Function types:', typeof window.openAIAssistant, typeof window.closeAIAssistant);