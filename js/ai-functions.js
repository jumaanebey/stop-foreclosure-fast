// AI Assistant Functions - Standalone file
console.log('AI Functions JavaScript loading...');

function openAIAssistant() {
    console.log('AI Assistant button clicked');
    const modal = document.getElementById('ai-assistant-modal');
    console.log('Modal element found:', modal);
    
    if (modal) {
        modal.style.display = 'flex';
        
        // Initialize the chatbot interface immediately
        initializeChatbot();
        
        console.log('Modal opened and chatbot initialized');
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

function initializeChatbot() {
    console.log('Initializing chatbot...');
    
    // Clear any existing static content and show the chatbot interface
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.style.display = 'none';
    }
    
    // Get or create the current slide container
    let currentSlide = document.getElementById('current-slide');
    if (!currentSlide) {
        // Create the chatbot interface if it doesn't exist
        const modalBody = document.querySelector('.ai-modal-body');
        if (modalBody) {
            modalBody.innerHTML = `
                <div class="chatbot-interface">
                    <div class="progress-container">
                        <div class="progress-dots" id="progress-dots"></div>
                    </div>
                    <div class="current-slide" id="current-slide">
                        <!-- Chatbot content will be inserted here -->
                    </div>
                </div>
            `;
        }
    }
    
    // Start the chatbot flow
    if (typeof startChatbot === 'function') {
        startChatbot();
    } else {
        // If startChatbot isn't available yet, start with step 1 directly
        showStep1();
    }
}

function showStep1() {
    console.log('Starting chatbot step 1');
    updateProgressDots(1, 5);
    
    const currentSlide = document.getElementById('current-slide');
    if (currentSlide) {
        currentSlide.innerHTML = `
            <div class="slide-question">What best describes your current situation?</div>
            <div class="slide-options">
                <div class="slide-option urgent" onclick="selectSituation('auction', 'fast')">
                    URGENT: My home is scheduled for auction/sale
                </div>
                <div class="slide-option urgent" onclick="selectSituation('default', 'fast')">
                    URGENT: I received a notice of default
                </div>
                <div class="slide-option" onclick="selectSituation('behind', 'slow')">
                    I'm behind on mortgage payments
                </div>
                <div class="slide-option" onclick="selectSituation('hardship', 'slow')">
                    I'm facing financial hardship
                </div>
                <div class="slide-option" onclick="selectSituation('exploring', 'slow')">
                    I'm exploring my options
                </div>
            </div>
        `;
    }
}

function updateProgressDots(current, total) {
    const progressContainer = document.getElementById('progress-dots');
    if (progressContainer) {
        let html = '';
        for (let i = 1; i <= total; i++) {
            html += `<div class="progress-dot ${i <= current ? 'active' : ''}">${i}</div>`;
        }
        progressContainer.innerHTML = html;
    }
}

function selectSituation(situation, path) {
    console.log('Situation selected:', situation, path);
    // This will need to connect to the main chatbot functions
    alert('Chatbot flow will continue here. Selected: ' + situation);
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