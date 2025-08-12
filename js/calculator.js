// Cash Offer Calculator JavaScript
let currentStep = 1;
let calculatorData = {
    property: {},
    condition: '',
    timeline: '',
    foreclosureStatus: '',
    offer: {}
};

document.addEventListener('DOMContentLoaded', function() {
    initializeCalculator();
});

function initializeCalculator() {
    // Set up condition card selection
    const conditionCards = document.querySelectorAll('.condition-card');
    conditionCards.forEach(card => {
        card.addEventListener('click', function() {
            selectCondition(this.dataset.value);
        });
    });
    
    // Set up timeline card selection
    const timelineCards = document.querySelectorAll('.timeline-card');
    timelineCards.forEach(card => {
        card.addEventListener('click', function() {
            selectTimeline(this.dataset.value);
        });
    });
    
    // Set up foreclosure status radio buttons
    const radioButtons = document.querySelectorAll('input[name="foreclosure-status"]');
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            calculatorData.foreclosureStatus = this.value;
            enableTimelineNext();
        });
    });
    
    // Set up form validation
    const requiredFields = document.querySelectorAll('#step-1 input[required], #step-1 select[required]');
    requiredFields.forEach(field => {
        field.addEventListener('change', validateStep1);
        field.addEventListener('input', validateStep1);
    });
    
    // Set up lead form submission
    const leadForm = document.getElementById('calculator-lead-form');
    if (leadForm) {
        leadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleLeadFormSubmission(this);
        });
    }
}

function nextStep(step) {
    if (!validateCurrentStep()) return;
    
    // Hide current step
    document.getElementById(`step-${currentStep}`).classList.remove('active');
    document.getElementById(`step-${currentStep}-indicator`).classList.remove('active');
    
    // Show next step
    currentStep = step;
    document.getElementById(`step-${currentStep}`).classList.add('active');
    document.getElementById(`step-${currentStep}-indicator`).classList.add('active');
    
    // Special handling for step 4 (results)
    if (step === 4) {
        calculateOffer();
    }
    
    // Track step progression
    if (typeof gtag !== 'undefined') {
        gtag('event', 'calculator_step_' + step, {
            'event_category': 'calculator',
            'event_label': 'step_progression'
        });
    }
    
    // Scroll to top of calculator
    document.querySelector('.calculator-section').scrollIntoView({ behavior: 'smooth' });
}

function prevStep(step) {
    // Hide current step
    document.getElementById(`step-${currentStep}`).classList.remove('active');
    document.getElementById(`step-${currentStep}-indicator`).classList.remove('active');
    
    // Show previous step
    currentStep = step;
    document.getElementById(`step-${currentStep}`).classList.add('active');
    document.getElementById(`step-${currentStep}-indicator`).classList.add('active');
    
    // Scroll to top of calculator
    document.querySelector('.calculator-section').scrollIntoView({ behavior: 'smooth' });
}

function validateCurrentStep() {
    switch(currentStep) {
        case 1:
            return validateStep1();
        case 2:
            return calculatorData.condition !== '';
        case 3:
            return calculatorData.timeline !== '' && calculatorData.foreclosureStatus !== '';
        default:
            return true;
    }
}

function validateStep1() {
    const address = document.getElementById('property-address').value;
    const type = document.getElementById('property-type').value;
    const sqft = document.getElementById('square-footage').value;
    const bedrooms = document.getElementById('bedrooms').value;
    const bathrooms = document.getElementById('bathrooms').value;
    
    const isValid = address && type && sqft && bedrooms && bathrooms;
    
    if (isValid) {
        calculatorData.property = {
            address,
            type,
            sqft,
            bedrooms,
            bathrooms
        };
    }
    
    return isValid;
}

function selectCondition(condition) {
    // Remove previous selection
    document.querySelectorAll('.condition-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Add selection to clicked card
    document.querySelector(`.condition-card[data-value="${condition}"]`).classList.add('selected');
    
    calculatorData.condition = condition;
    document.getElementById('condition-next').disabled = false;
}

function selectTimeline(timeline) {
    // Remove previous selection
    document.querySelectorAll('.timeline-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Add selection to clicked card
    document.querySelector(`.timeline-card[data-value="${timeline}"]`).classList.add('selected');
    
    calculatorData.timeline = timeline;
    enableTimelineNext();
}

function enableTimelineNext() {
    const timelineNext = document.getElementById('timeline-next');
    if (calculatorData.timeline !== '' && calculatorData.foreclosureStatus !== '') {
        timelineNext.disabled = false;
    }
}

function calculateOffer() {
    // Show loading state
    document.getElementById('calculating').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    
    // Simulate calculation delay
    setTimeout(() => {
        const offer = generateOffer();
        displayResults(offer);
        
        // Hide loading and show results
        document.getElementById('calculating').style.display = 'none';
        document.getElementById('results').style.display = 'block';
        
        // Track offer calculation
        if (typeof gtag !== 'undefined') {
            gtag('event', 'offer_calculated', {
                'event_category': 'calculator',
                'event_label': 'offer_generated',
                'value': offer.amount
            });
        }
    }, 3000);
}

function generateOffer() {
    // Base market value estimation (simplified)
    let baseValue = getBaseValue();
    
    // Apply condition adjustments
    let conditionMultiplier = getConditionMultiplier();
    let adjustedValue = baseValue * conditionMultiplier;
    
    // Apply timeline adjustments
    let timelineMultiplier = getTimelineMultiplier();
    let finalValue = adjustedValue * timelineMultiplier;
    
    // Apply foreclosure urgency
    if (calculatorData.foreclosureStatus === 'yes') {
        finalValue *= 1.02; // 2% urgency premium
    }
    
    // Calculate range (±5%)
    let minOffer = Math.round(finalValue * 0.95);
    let maxOffer = Math.round(finalValue * 1.05);
    let avgOffer = Math.round(finalValue);
    
    return {
        amount: avgOffer,
        min: minOffer,
        max: maxOffer,
        marketValue: Math.round(baseValue),
        conditionAdjustment: Math.round(baseValue - adjustedValue),
        repairEstimate: Math.round(baseValue * 0.05), // 5% repair allowance
        closingCosts: Math.round(baseValue * 0.03) // 3% closing costs we pay
    };
}

function getBaseValue() {
    // Simplified market value calculation
    let baseValue = 500000; // Default CA home value
    
    // Adjust by size
    switch(calculatorData.property.sqft) {
        case 'under-1000': baseValue = 400000; break;
        case '1000-1500': baseValue = 500000; break;
        case '1500-2000': baseValue = 600000; break;
        case '2000-2500': baseValue = 750000; break;
        case '2500-3000': baseValue = 900000; break;
        case 'over-3000': baseValue = 1200000; break;
    }
    
    // Adjust by bedrooms
    const bedroomMultiplier = {
        '1': 0.8,
        '2': 0.9,
        '3': 1.0,
        '4': 1.15,
        '5+': 1.3
    };
    
    baseValue *= (bedroomMultiplier[calculatorData.property.bedrooms] || 1);
    
    // Add randomness to make it feel more realistic
    const variance = 0.9 + (Math.random() * 0.2); // ±10% variance
    return Math.round(baseValue * variance);
}

function getConditionMultiplier() {
    const conditionMultipliers = {
        'excellent': 1.12, // +12%
        'good': 1.02,      // +2%
        'fair': 0.88,      // -12%
        'poor': 0.75       // -25%
    };
    
    return conditionMultipliers[calculatorData.condition] || 0.9;
}

function getTimelineMultiplier() {
    const timelineMultipliers = {
        'immediate': 1.05, // +5% urgency premium
        'fast': 1.0,       // Standard
        'flexible': 1.02   // +2% for flexibility
    };
    
    return timelineMultipliers[calculatorData.timeline] || 1.0;
}

function displayResults(offer) {
    calculatorData.offer = offer;
    
    // Update offer amounts
    document.getElementById('offer-amount').textContent = formatCurrency(offer.amount);
    document.getElementById('offer-min').textContent = offer.min.toLocaleString();
    document.getElementById('offer-max').textContent = offer.max.toLocaleString();
    document.getElementById('final-offer').textContent = formatCurrency(offer.amount);
    document.getElementById('cash-proceeds').textContent = formatCurrency(offer.amount);
    
    // Update breakdown
    document.getElementById('market-value').textContent = formatCurrency(offer.marketValue);
    document.getElementById('condition-adjustment').textContent = formatCurrency(-Math.abs(offer.conditionAdjustment));
    document.getElementById('repair-estimates').textContent = formatCurrency(-offer.repairEstimate);
    document.getElementById('closing-costs').textContent = '+' + formatCurrency(offer.closingCosts);
}

function formatCurrency(amount) {
    return '$' + Math.abs(amount).toLocaleString();
}

function handleLeadFormSubmission(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Show loading state
    const submitButton = form.querySelector('.calc-submit-button');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Submitting...';
    submitButton.disabled = true;
    
    // Combine calculator data with lead data
    const leadData = {
        ...data,
        type: 'calculator_lead',
        offer_amount: calculatorData.offer.amount,
        property_address: calculatorData.property.address,
        property_type: calculatorData.property.type,
        property_condition: calculatorData.condition,
        timeline: calculatorData.timeline,
        foreclosure_status: calculatorData.foreclosureStatus,
        square_footage: calculatorData.property.sqft,
        bedrooms: calculatorData.property.bedrooms,
        bathrooms: calculatorData.property.bathrooms
    };
    
    // Analytics events
    if (typeof fbq !== 'undefined') {
        fbq('track', 'Lead');
    }
    
    if (typeof gtag !== 'undefined') {
        gtag('event', 'generate_lead', {
            'event_category': 'calculator',
            'event_label': 'official_offer_request',
            'value': calculatorData.offer.amount
        });
    }
    
    // Submit to Google Sheets (using same endpoint as other forms)
    submitToGoogleSheets(leadData)
        .then(() => {
            // Show success message
            showSuccessMessage();
        })
        .catch(error => {
            console.error('Calculator lead submission error:', error);
            alert('There was an error submitting your request. Please text us at (949) 328-4811 for immediate assistance.');
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        });
}

function submitToGoogleSheets(data) {
    // Use the same Google Apps Script URL from the main script
    const GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycby8VHy6p65YC17hxjdAX5Hk7d5l4d7uyDHMZy9I7vMJY_RHwa5lw2DzstoXtyJvTdT9/exec';
    
    return fetch(GOOGLE_SCRIPT_URL, {
        method: 'POST',
        mode: 'no-cors',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
}

function showSuccessMessage() {
    const form = document.getElementById('calculator-lead-form');
    form.innerHTML = `
        <div class="success-message">
            <div class="success-icon">✅</div>
            <h3>Request Submitted Successfully!</h3>
            <p>We'll contact you within 2 hours during business hours with your official written offer.</p>
            <p><strong>Need immediate help?</strong></p>
            <div class="success-actions">
                <a href="sms:+1-949-328-4811?body=I just used your calculator and got an estimate of ${formatCurrency(calculatorData.offer.amount)} for my property. I'd like to discuss this further." class="success-button">
                    💬 Text Now: (949) 328-4811
                </a>
                <a href="index.html#schedule" class="success-button secondary">
                    📅 Schedule Call
                </a>
            </div>
        </div>
    `;
    
    // Track successful submission
    if (typeof gtag !== 'undefined') {
        gtag('event', 'conversion', {
            'event_category': 'calculator',
            'event_label': 'lead_captured'
        });
    }
}

function startOver() {
    // Reset calculator data
    calculatorData = {
        property: {},
        condition: '',
        timeline: '',
        foreclosureStatus: '',
        offer: {}
    };
    
    // Reset form
    document.getElementById('property-address').value = '';
    document.getElementById('property-type').value = '';
    document.getElementById('square-footage').value = '';
    document.getElementById('bedrooms').value = '';
    document.getElementById('bathrooms').value = '';
    
    // Clear selections
    document.querySelectorAll('.condition-card, .timeline-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    document.querySelectorAll('input[name="foreclosure-status"]').forEach(radio => {
        radio.checked = false;
    });
    
    // Go back to step 1
    document.querySelectorAll('.calculator-step').forEach(step => {
        step.classList.remove('active');
    });
    document.querySelectorAll('.step').forEach(indicator => {
        indicator.classList.remove('active');
    });
    
    currentStep = 1;
    document.getElementById('step-1').classList.add('active');
    document.getElementById('step-1-indicator').classList.add('active');
    
    // Scroll to top
    document.querySelector('.calculator-section').scrollIntoView({ behavior: 'smooth' });
}