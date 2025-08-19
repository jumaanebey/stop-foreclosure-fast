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

// Chatbot data storage
let chatbotData = {};
let urgencyPath = 'slow';
let currentStep = 1;

function selectSituation(situation, path) {
    console.log('Situation selected:', situation, path);
    chatbotData.situation = situation;
    urgencyPath = path;
    
    // Move to step 2
    showStep2();
}

function showStep2() {
    currentStep = 2;
    updateProgressDots(2, 5);
    
    const currentSlide = document.getElementById('current-slide');
    if (!currentSlide) return;
    
    if (urgencyPath === 'fast') {
        currentSlide.innerHTML = `
            <div class="slide-question">When do you need to take action? <span class="urgency-indicator urgency-critical">URGENT</span></div>
            <div class="slide-options">
                <div class="slide-option urgent" onclick="selectTimeline('days', 'CRITICAL_RISK')">
                    CRITICAL: Days - Auction is very soon
                </div>
                <div class="slide-option urgent" onclick="selectTimeline('weeks', 'CRITICAL_RISK')">
                    URGENT: Weeks - I have some time but not much
                </div>
                <div class="slide-option" onclick="selectTimeline('month', 'HIGH_RISK')">
                    About a month
                </div>
                <div class="slide-option" onclick="selectTimeline('unsure', 'HIGH_RISK')">
                    I'm not sure of the timeline
                </div>
            </div>
        `;
    } else {
        currentSlide.innerHTML = `
            <div class="slide-question">How urgent do you feel your situation is?</div>
            <div class="slide-options">
                <div class="slide-option" onclick="selectTimeline('urgent', 'HIGH_RISK')">
                    Very urgent - need help soon
                </div>
                <div class="slide-option" onclick="selectTimeline('concerned', 'MODERATE_RISK')">
                    Concerned but have some time
                </div>
                <div class="slide-option" onclick="selectTimeline('planning', 'MODERATE_RISK')">
                    Planning ahead
                </div>
                <div class="slide-option" onclick="selectTimeline('exploring', 'EARLY_STAGE')">
                    Just exploring options
                </div>
            </div>
        `;
    }
}

function selectTimeline(timeline, riskLevel) {
    console.log('Timeline selected:', timeline, riskLevel);
    chatbotData.timeline = timeline;
    chatbotData.riskLevel = riskLevel;
    
    // Move to step 3
    showStep3();
}

function showStep3() {
    currentStep = 3;
    updateProgressDots(3, 5);
    
    const currentSlide = document.getElementById('current-slide');
    if (!currentSlide) return;
    
    currentSlide.innerHTML = `
        <div class="slide-question">What's your name?</div>
        <div class="slide-input">
            <input type="text" id="step3-name" placeholder="Enter your first name" maxlength="50">
            <button onclick="saveName()" class="slide-button">Next</button>
        </div>
    `;
    
    // Focus on the input
    setTimeout(() => {
        const input = document.getElementById('step3-name');
        if (input) input.focus();
    }, 100);
}

function saveName() {
    const nameInput = document.getElementById('step3-name');
    const name = nameInput ? nameInput.value.trim() : '';
    
    if (!name) {
        alert('Please enter your name to continue.');
        return;
    }
    
    chatbotData.name = name;
    console.log('Name saved:', name);
    
    // Move to step 4
    showStep4();
}

function showStep4() {
    currentStep = 4;
    updateProgressDots(4, 5);
    
    const currentSlide = document.getElementById('current-slide');
    if (!currentSlide) return;
    
    currentSlide.innerHTML = `
        <div class="slide-question">What's the best phone number to reach you?</div>
        <div class="slide-input">
            <input type="tel" id="step4-phone" placeholder="(555) 123-4567" maxlength="20">
            <button onclick="savePhone()" class="slide-button">Next</button>
        </div>
    `;
    
    // Focus on the input
    setTimeout(() => {
        const input = document.getElementById('step4-phone');
        if (input) input.focus();
    }, 100);
}

function savePhone() {
    const phoneInput = document.getElementById('step4-phone');
    const phone = phoneInput ? phoneInput.value.trim() : '';
    
    if (!phone) {
        alert('Please enter your phone number to continue.');
        return;
    }
    
    chatbotData.phone = phone;
    console.log('Phone saved:', phone);
    
    // Move to email step
    showStep4Email();
}

function showStep4Email() {
    updateProgressDots(4, 5);
    
    const currentSlide = document.getElementById('current-slide');
    if (!currentSlide) return;
    
    currentSlide.innerHTML = `
        <div class="slide-question">What's your email address? (optional)</div>
        <div class="slide-input">
            <input type="email" id="step4-email" placeholder="your@email.com">
            <button onclick="saveEmail()" class="slide-button">Next</button>
            <button onclick="skipEmail()" style="background: #6b7280; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 14px;">Skip</button>
        </div>
        <p style="font-size: 14px; color: #6b7280; text-align: center; margin-top: 10px;">
            We'll use this to send you appointment confirmation and helpful resources.
        </p>
    `;
    
    // Focus on the input
    setTimeout(() => {
        const input = document.getElementById('step4-email');
        if (input) input.focus();
    }, 100);
}

function saveEmail() {
    const emailInput = document.getElementById('step4-email');
    const email = emailInput ? emailInput.value.trim() : '';
    
    chatbotData.email = email;
    console.log('Email saved:', email);
    
    // Move to step 5
    showStep5();
}

function skipEmail() {
    console.log('Email skipped');
    chatbotData.email = '';
    
    // Move to step 5
    showStep5();
}

function showStep5() {
    currentStep = 5;
    updateProgressDots(5, 5);
    
    const currentSlide = document.getElementById('current-slide');
    if (!currentSlide) return;
    
    const isEmergency = chatbotData.riskLevel === 'CRITICAL_RISK';
    
    currentSlide.innerHTML = `
        <div class="slide-question">Perfect! Let's schedule your consultation.</div>
        <div class="consultation-summary">
            <p><strong>Name:</strong> ${chatbotData.name}</p>
            <p><strong>Phone:</strong> ${chatbotData.phone}</p>
            ${chatbotData.email ? `<p><strong>Email:</strong> ${chatbotData.email}</p>` : ''}
            <p><strong>Priority Level:</strong> ${chatbotData.riskLevel || 'Standard'}</p>
            <p><strong>Situation:</strong> ${getSituationText(chatbotData.situation)}</p>
        </div>
        <div class="calendar-section" id="calendar-section">
            <!-- Calendar will be inserted here -->
        </div>
        <div style="text-align: center; margin: 15px 0;">
            <p style="font-size: 14px; color: #6b7280;">
                Choose your appointment time above, then click Complete Booking below.
            </p>
        </div>
        <button onclick="completeBooking()" class="slide-button" style="background: #059669;">Complete Booking</button>
    `;
    
    // Insert calendar
    generateCalendar(isEmergency);
}

function generateCalendar(isEmergency) {
    const calendarSection = document.getElementById('calendar-section');
    if (!calendarSection) return;
    
    const calendarUrl = 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ11saPKXhTtJ5jLw6q9XASJXT6whF2LSN7MgXGzcT9PIlyRhXWXVVIDKqsIojgwkJo76HPcFLSz?gv=true';
    
    const urgencyMessage = isEmergency 
        ? '<div style="background: #fef2f2; padding: 15px; border-radius: 8px; border-left: 4px solid #dc2626; margin-bottom: 20px;">' +
             '<p style="margin: 0; color: #dc2626; font-weight: 600;">🚨 EMERGENCY Priority Scheduling</p>' +
             '<p style="margin: 5px 0 0 0; color: #991b1b; font-size: 14px;">Same-day appointments available. Please mention this is an emergency consultation when booking.</p>' +
           '</div>'
        : '<div style="background: #f0fdf4; padding: 15px; border-radius: 8px; border-left: 4px solid #10b981; margin-bottom: 20px;">' +
             '<p style="margin: 0; color: #065f46; font-weight: 600;">📅 Standard Consultation Scheduling</p>' +
             '<p style="margin: 5px 0 0 0; color: #047857; font-size: 14px;">Select a convenient time for your foreclosure consultation.</p>' +
           '</div>';
    
    // Create embedded calendar iframe
    calendarSection.innerHTML = urgencyMessage +
        '<div style="border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; margin: 20px 0;">' +
            '<iframe src="' + calendarUrl + '" ' +
                'style="width: 100%; height: 400px; border: none; background: white;" ' +
                'frameborder="0" ' +
                'scrolling="auto">' +
            '</iframe>' +
        '</div>' +
        '<div style="text-align: center; margin: 15px 0;">' +
            '<p style="font-size: 14px; color: #6b7280; margin: 0;">Can\'t see the calendar? ' +
            '<a href="' + calendarUrl + '" target="_blank" style="color: #0ea5e9; text-decoration: none;">Open in new window</a></p>' +
        '</div>';
    
    // Try to load Google Calendar scheduling button if available
    setTimeout(() => {
        if (window.calendar && window.calendar.schedulingButton) {
            const buttonContainer = document.createElement('div');
            buttonContainer.id = 'google-calendar-button-container';
            buttonContainer.style.textAlign = 'center';
            buttonContainer.style.marginTop = '15px';
            
            calendarSection.appendChild(buttonContainer);
            
            window.calendar.schedulingButton.load({
                url: calendarUrl,
                color: isEmergency ? '#dc2626' : '#0ea5e9',
                label: isEmergency ? '🚨 Schedule Emergency Consultation' : '📅 Schedule Consultation',
                target: buttonContainer,
            });
        }
    }, 1000);
}

function completeBooking() {
    console.log('Completing booking with data:', chatbotData);
    
    // Submit to backend
    submitLeadToDashboard();
    
    // Show success message
    const currentSlide = document.getElementById('current-slide');
    if (currentSlide) {
        currentSlide.innerHTML = `
            <div class="success-message">
                <h3 style="color: #059669; margin-bottom: 15px;">Consultation Scheduled!</h3>
                <p><strong>${chatbotData.name}</strong>, we've received your information and will contact you at <strong>${chatbotData.phone}</strong> within the next hour.</p>
                <p style="margin-top: 20px;">
                    <strong>Emergency?</strong> Call us now: <a href="tel:+1-949-328-4811" style="color: #dc2626; font-weight: bold;">(949) 328-4811</a>
                </p>
                <button onclick="closeAIAssistant()" class="slide-button" style="background: #059669;">Close</button>
            </div>
        `;
    }
}

async function submitLeadToDashboard() {
    try {
        const response = await fetch('https://stop-foreclosure-fast.onrender.com/api/ai/emergency-booking', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: chatbotData.name,
                phone: chatbotData.phone,
                ai_situation: chatbotData.situation,
                urgency_level: chatbotData.riskLevel,
                lead_source: 'ai_chatbot',
                timestamp: new Date().toISOString()
            })
        });
        
        const result = await response.json();
        console.log('Lead submitted successfully:', result);
    } catch (error) {
        console.error('Error submitting lead:', error);
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

// Helper function to get readable situation text
function getSituationText(situation) {
    const situations = {
        'auction': 'Home scheduled for auction/sale',
        'default': 'Received notice of default',
        'behind': 'Behind on mortgage payments',
        'hardship': 'Facing financial hardship',
        'exploring': 'Exploring options'
    };
    return situations[situation] || situation;
}

// Make functions globally available immediately
window.openAIAssistant = openAIAssistant;
window.closeAIAssistant = closeAIAssistant;

console.log('AI functions defined and assigned to window');
console.log('Function types:', typeof window.openAIAssistant, typeof window.closeAIAssistant);