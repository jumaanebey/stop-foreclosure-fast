// AI Assistant Functions - Standalone file
console.log('AI Functions JavaScript loading...');

// Add CSS for spinner animation
const spinnerCSS = `
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
`;

// Add CSS to head
const style = document.createElement('style');
style.textContent = spinnerCSS;
document.head.appendChild(style);

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
    
    // Get the modal body and completely replace its content
    const modalBody = document.getElementById('ai-modal-body');
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
    
    // Start with step 1 directly
    showStep1();
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
    
    // Move to address collection step
    showStep4Address();
}

function skipEmail() {
    console.log('Email skipped');
    chatbotData.email = '';
    
    // Move to address collection step
    showStep4Address();
}

function showStep4Address() {
    updateProgressDots(4, 5);
    
    const currentSlide = document.getElementById('current-slide');
    if (!currentSlide) return;
    
    currentSlide.innerHTML = `
        <div class="slide-question">What's the property address we'll be discussing?</div>
        <div class="slide-input">
            <input type="text" id="step4-street" placeholder="123 Main Street" style="margin-bottom: 10px;">
            <div style="display: grid; grid-template-columns: 1fr 100px 100px; gap: 10px;">
                <input type="text" id="step4-city" placeholder="City">
                <input type="text" id="step4-state" placeholder="State" maxlength="2">
                <input type="text" id="step4-zip" placeholder="Zip" maxlength="10">
            </div>
            <button onclick="saveAddress()" class="slide-button">Next</button>
        </div>
        <p style="font-size: 14px; color: #6b7280; text-align: center; margin-top: 10px;">
            This helps us provide more accurate guidance for your specific situation.
        </p>
    `;
    
    // Focus on the street input
    setTimeout(() => {
        const input = document.getElementById('step4-street');
        if (input) input.focus();
    }, 100);
}

async function saveAddress() {
    const streetInput = document.getElementById('step4-street');
    const cityInput = document.getElementById('step4-city');
    const stateInput = document.getElementById('step4-state');
    const zipInput = document.getElementById('step4-zip');
    
    const street = streetInput ? streetInput.value.trim() : '';
    const city = cityInput ? cityInput.value.trim() : '';
    const state = stateInput ? stateInput.value.trim().toUpperCase() : '';
    const zip = zipInput ? zipInput.value.trim() : '';
    
    if (!street || !city || !state || !zip) {
        alert('Please fill in all address fields to continue.');
        return;
    }
    
    // Save address data
    chatbotData.propertyAddress = {
        street: street,
        city: city,
        state: state,
        zip: zip,
        full: `${street}, ${city}, ${state} ${zip}`
    };
    
    console.log('Address saved:', chatbotData.propertyAddress);
    
    // Show loading message while looking up foreclosure data
    const currentSlide = document.getElementById('current-slide');
    if (currentSlide) {
        currentSlide.innerHTML = `
            <div class="slide-question">Looking up foreclosure data for your area...</div>
            <div style="text-align: center; padding: 20px;">
                <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #0ea5e9; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <p style="margin-top: 15px; color: #6b7280;">
                    Getting local market insights to better assist you...
                </p>
            </div>
        `;
    }
    
    // Lookup foreclosure data for the area
    try {
        await lookupForeclosureData(chatbotData.propertyAddress);
    } catch (error) {
        console.log('Foreclosure data lookup failed:', error);
    }
    
    // Move to final step
    setTimeout(() => showStep5(), 2000);
}

async function lookupForeclosureData(addressData) {
    try {
        const response = await fetch('https://stop-foreclosure-fast.onrender.com/api/foreclosure/area-insights', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                address: addressData.full,
                zip_code: addressData.zip,
                city: addressData.city,
                state: addressData.state
            })
        });
        
        const data = await response.json();
        if (data.success && data.area_insights) {
            chatbotData.foreclosureInsights = data.area_insights;
            console.log('Foreclosure insights received:', data.area_insights);
            
            // Show market insights to user
            showMarketInsights(data.area_insights);
        }
    } catch (error) {
        console.log('Failed to lookup foreclosure data:', error);
    }
}

function showMarketInsights(insights) {
    const currentSlide = document.getElementById('current-slide');
    if (!currentSlide) return;
    
    const marketMessage = insights.market_message || 'We\'ve analyzed your local area.';
    const riskLevel = insights.risk_level || 'standard';
    const activityLevel = insights.market_activity || 'low';
    
    // Apply urgency modifier to existing risk level if data shows high foreclosure activity
    if (insights.urgency_modifier && insights.urgency_modifier > 1.2) {
        if (chatbotData.riskLevel === 'MODERATE_RISK') {
            chatbotData.riskLevel = 'HIGH_RISK';
        } else if (chatbotData.riskLevel === 'EARLY_STAGE') {
            chatbotData.riskLevel = 'MODERATE_RISK';
        }
        console.log('Risk level upgraded based on local market data:', chatbotData.riskLevel);
    }
    
    let activityColor = '#059669'; // green
    let activityIcon = '🟢';
    if (activityLevel === 'high') {
        activityColor = '#dc2626'; // red
        activityIcon = '🔴';
    } else if (activityLevel === 'moderate') {
        activityColor = '#d97706'; // orange
        activityIcon = '🟡';
    }
    
    currentSlide.innerHTML = `
        <div class="slide-question">Local Market Analysis</div>
        <div style="background: #f8fafc; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 4px solid ${activityColor};">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 24px; margin-right: 10px;">${activityIcon}</span>
                <h4 style="margin: 0; color: ${activityColor};">
                    ${activityLevel.charAt(0).toUpperCase() + activityLevel.slice(1)} Foreclosure Activity
                </h4>
            </div>
            <p style="margin: 10px 0; line-height: 1.5;">
                ${marketMessage}
            </p>
            ${insights.total_properties ? `
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; font-size: 14px;">
                    <div style="text-align: center; padding: 10px; background: white; border-radius: 6px;">
                        <div style="font-weight: bold; color: #374151;">${insights.total_properties}</div>
                        <div style="color: #6b7280;">Total Properties</div>
                    </div>
                    <div style="text-align: center; padding: 10px; background: white; border-radius: 6px;">
                        <div style="font-weight: bold; color: #374151;">${insights.recent_activity || 0}</div>
                        <div style="color: #6b7280;">Recent Activity</div>
                    </div>
                </div>
            ` : ''}
        </div>
        <button onclick="continueToScheduling()" class="slide-button">Continue to Scheduling</button>
    `;
}

function continueToScheduling() {
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
                email: chatbotData.email || '',
                property_address: chatbotData.propertyAddress ? chatbotData.propertyAddress.full : '',
                ai_situation: getSituationText(chatbotData.situation),
                urgency_level: chatbotData.riskLevel,
                foreclosure_insights: chatbotData.foreclosureInsights || null,
                lead_source: 'ai_chatbot_with_foreclosure_data',
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