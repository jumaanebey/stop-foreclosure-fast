// Cash Offer Calculator JavaScript
let currentStep = 1;
let calculatorData = {
    property: {},
    condition: '',
    desiredPrice: 0,
    timeline: '',
    foreclosureStatus: ''
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
    
    // Set up price input validation with formatting
    const priceInput = document.getElementById('desired-price');
    if (priceInput) {
        priceInput.addEventListener('input', function() {
            // Remove non-numeric characters except for the initial value
            let value = this.value.replace(/[^\d]/g, '');
            
            if (value) {
                // Store the numeric value
                calculatorData.desiredPrice = parseInt(value) || 0;
                
                // Format and display with dollar sign and commas
                this.value = '$' + parseInt(value).toLocaleString();
            } else {
                calculatorData.desiredPrice = 0;
                this.value = '';
            }
            
            // Clear any selected quick price buttons when typing
            document.querySelectorAll('.price-range-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            
            enableTimelineNext();
        });
        
        // Handle focus to allow editing
        priceInput.addEventListener('focus', function() {
            // Remove formatting when focused for easier editing
            if (calculatorData.desiredPrice > 0) {
                this.value = calculatorData.desiredPrice.toString();
            }
        });
        
        // Handle blur to restore formatting
        priceInput.addEventListener('blur', function() {
            if (calculatorData.desiredPrice > 0) {
                this.value = '$' + calculatorData.desiredPrice.toLocaleString();
            }
        });
    }
    
    // Set up quick price selection buttons
    const priceButtons = document.querySelectorAll('.price-range-btn');
    priceButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.classList.contains('custom-btn')) {
                // Custom button - focus on input field
                selectCustomPrice();
            } else {
                // Quick price selection
                const price = parseInt(this.dataset.price);
                selectQuickPrice(price, this);
            }
        });
    });
    
    // Set up timeline radio selection
    const timelineRadios = document.querySelectorAll('input[name="timeline"]');
    timelineRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            calculatorData.timeline = this.value;
            enableTimelineNext();
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
    
    // Special handling for step 4 (summary)
    if (step === 4) {
        displaySummary();
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
            return calculatorData.desiredPrice > 0 && calculatorData.timeline !== '' && calculatorData.foreclosureStatus !== '';
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


function selectQuickPrice(price, buttonElement) {
    // Clear all previous selections
    document.querySelectorAll('.price-range-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Select the clicked button
    buttonElement.classList.add('selected');
    
    // Update the price input and data
    const priceInput = document.getElementById('desired-price');
    priceInput.value = '$' + price.toLocaleString();
    calculatorData.desiredPrice = price;
    
    // Enable next step if other conditions are met
    enableTimelineNext();
    
    // Track quick price selection
    if (typeof gtag !== 'undefined') {
        gtag('event', 'quick_price_select', {
            'event_category': 'calculator',
            'event_label': 'price_button_clicked',
            'value': price
        });
    }
}

function selectCustomPrice() {
    // Clear all quick price selections
    document.querySelectorAll('.price-range-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Highlight custom button and focus input
    const customBtn = document.querySelector('.price-range-btn.custom-btn');
    customBtn.classList.add('selected');
    
    const priceInput = document.getElementById('desired-price');
    priceInput.focus();
    priceInput.select();
    
    // Track custom price selection
    if (typeof gtag !== 'undefined') {
        gtag('event', 'custom_price_select', {
            'event_category': 'calculator',
            'event_label': 'custom_button_clicked'
        });
    }
}

function enableTimelineNext() {
    const timelineNext = document.getElementById('timeline-next');
    if (calculatorData.desiredPrice > 0 && calculatorData.timeline !== '' && calculatorData.foreclosureStatus !== '') {
        timelineNext.disabled = false;
    }
}

function displaySummary() {
    // Show the summary section
    document.getElementById('request-summary').style.display = 'block';
    
    // Populate summary fields
    document.getElementById('summary-address').textContent = calculatorData.property.address || '-';
    document.getElementById('summary-type').textContent = formatPropertyType(calculatorData.property.type);
    document.getElementById('summary-size').textContent = formatSquareFootage(calculatorData.property.sqft);
    document.getElementById('summary-condition').textContent = formatCondition(calculatorData.condition);
    document.getElementById('summary-price').textContent = formatCurrency(calculatorData.desiredPrice);
    document.getElementById('summary-timeline').textContent = formatTimeline(calculatorData.timeline);
    document.getElementById('summary-foreclosure').textContent = formatForeclosureStatus(calculatorData.foreclosureStatus);
    
    // Track summary view
    if (typeof gtag !== 'undefined') {
        gtag('event', 'summary_viewed', {
            'event_category': 'calculator',
            'event_label': 'request_summary',
            'value': calculatorData.desiredPrice
        });
    }
}

// Formatting functions for the summary display
function formatPropertyType(type) {
    const types = {
        'single-family': 'Single Family Home',
        'townhouse': 'Townhouse',
        'condo': 'Condominium',
        'multi-family': 'Multi-Family',
        'mobile-home': 'Mobile Home',
        'other': 'Other'
    };
    return types[type] || type;
}

function formatSquareFootage(sqft) {
    const sizes = {
        'under-1000': 'Under 1,000 sq ft',
        '1000-1500': '1,000 - 1,500 sq ft',
        '1500-2000': '1,500 - 2,000 sq ft',
        '2000-2500': '2,000 - 2,500 sq ft',
        '2500-3000': '2,500 - 3,000 sq ft',
        'over-3000': 'Over 3,000 sq ft'
    };
    return sizes[sqft] || sqft;
}

function formatCondition(condition) {
    const conditions = {
        'excellent': 'Excellent',
        'good': 'Good', 
        'fair': 'Fair',
        'poor': 'Needs Work'
    };
    return conditions[condition] || condition;
}

function formatTimeline(timeline) {
    const timelines = {
        'immediate': 'Immediate (1-2 weeks)',
        'fast': 'Fast (1-2 months)',
        'flexible': 'Flexible (2-6 months)'
    };
    return timelines[timeline] || timeline;
}

function formatForeclosureStatus(status) {
    const statuses = {
        'yes': 'Currently in foreclosure',
        'behind': 'Behind on payments',
        'no': 'Current on payments'
    };
    return statuses[status] || status;
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
        type: 'cash_offer_request',
        desired_price: calculatorData.desiredPrice,
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
            'event_label': 'cash_offer_request',
            'value': calculatorData.desiredPrice
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
    const GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwiaTZKcl3dgGbZ399lBokTOkkZXnQvQJqWqen_Nc7Io-dGscxC0wLKly1spMXDwB4G/exec';
    
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
            <h3>Cash Offer Request Submitted!</h3>
            <p>We'll review your property details and contact you within 2 hours during business hours with our best cash offer based on your desired price of ${formatCurrency(calculatorData.desiredPrice)}.</p>
            <p><strong>Need immediate help?</strong></p>
            <div class="success-actions">
                <a href="sms:+1-949-328-4811?body=I just submitted a cash offer request for ${formatCurrency(calculatorData.desiredPrice)} for my property. I'd like to discuss this further." class="success-button">
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
        desiredPrice: 0,
        timeline: '',
        foreclosureStatus: ''
    };
    
    // Reset form
    document.getElementById('property-address').value = '';
    document.getElementById('property-type').value = '';
    document.getElementById('square-footage').value = '';
    document.getElementById('bedrooms').value = '';
    document.getElementById('bathrooms').value = '';
    
    // Reset price input
    const priceInput = document.getElementById('desired-price');
    if (priceInput) priceInput.value = '';
    
    // Clear selections
    document.querySelectorAll('.condition-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    document.querySelectorAll('.price-range-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    document.querySelectorAll('input[name="foreclosure-status"], input[name="timeline"]').forEach(radio => {
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