// Form handling and analytics
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contact-form');
    const leadMagnetForm = document.getElementById('lead-magnet-form');
    const exitPopupForm = document.getElementById('exit-popup-form');
    const emergencyContactForm = document.getElementById('emergency-contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmission(this);
        });
    }
    
    if (leadMagnetForm) {
        leadMagnetForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleLeadMagnetSubmission(this);
        });
    }
    
    if (exitPopupForm) {
        exitPopupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleExitPopupSubmission(this);
        });
    }
    
    if (emergencyContactForm) {
        emergencyContactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleEmergencyContactSubmission(this);
        });
    }
    
    // Initialize exit intent detection
    initExitIntent();
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Phone number tracking
    document.querySelectorAll('a[href^="tel:"]').forEach(phoneLink => {
        phoneLink.addEventListener('click', function() {
            // Facebook Pixel event
            if (typeof fbq !== 'undefined') {
                fbq('track', 'Contact');
            }
            // Google Analytics event
            if (typeof gtag !== 'undefined') {
                gtag('event', 'phone_call', {
                    'event_category': 'engagement',
                    'event_label': 'header_phone'
                });
            }
        });
    });
});

function handleFormSubmission(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Add form type and tracking data
    data.form_type = 'contact';
    data.urgency_level = determineUrgencyLevel(data);
    data.session_data = getSessionTrackingData();
    data.lead_source = getTrafficSource();
    data.device_type = getDeviceType();
    
    // Show loading state
    const submitButton = form.querySelector('.submit-button');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Submitting...';
    submitButton.disabled = true;
    
    // Track form completion in analytics
    if (typeof gtag !== 'undefined') {
        gtag('event', 'form_completion', {
            'event_category': 'Virtual Consultation',
            'event_label': 'contact_form',
            'value': 50
        });
    }
    
    // Update lead score
    if (typeof updateLeadScore === 'function') {
        updateLeadScore('form_completion', {
            formType: 'contact',
            data: data
        });
    }
    
    // Submit to advanced lead capture system
    submitToAdvancedSystem(data)
        .then(response => {
            // Store lead ID for tracking
            if (response.lead_id) {
                sessionStorage.setItem('leadId', response.lead_id);
            }
            
            // Track conversion events
            if (typeof fbq !== 'undefined') {
                fbq('track', 'Lead', {
                    content_name: 'Foreclosure Consultation Request',
                    content_category: 'Lead Generation',
                    value: response.score || 50
                });
            }
            
            // Redirect to appropriate thank you page based on priority
            const thankYouPage = response.priority === 'P1' || response.priority === 'P2' 
                ? 'thank-you-priority.html' 
                : 'thank-you.html';
            
            window.location.href = `${thankYouPage}?score=${response.score}&priority=${response.priority}`;
        })
        .catch(error => {
            console.error('Form submission error:', error);
            
            // Fallback to basic submission
            submitToGoogleSheets(data)
                .then(() => {
                    window.location.href = 'thank-you.html';
                })
                .catch(() => {
                    alert('There was an error submitting your form. Please text us at (949) 565-5285 for immediate assistance.');
                    submitButton.textContent = originalText;
                    submitButton.disabled = false;
                });
        });
}

function submitToGoogleSheets(data) {
    // Google Apps Script Web App URL for contact form (Simplified ConvertKit integration)
    const GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwot6SWKdQKzoOmVizO8_mh93aU_A6cIkGnpu5yrnzmPrfkn4pDQ7E07asi1_PXSpsq/exec';
    
    return fetch(GOOGLE_SCRIPT_URL, {
        method: 'POST',
        mode: 'no-cors',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
}

// Alternative email submission function
function submitViaEmail(data) {
    const subject = 'New Lead from Stop Foreclosure Fast';
    const body = `
New lead submission:

Name: ${data.name}
Email: ${data.email}
Phone: ${data.phone}
Address: ${data.address}
Situation: ${data.situation}

Submitted: ${new Date().toLocaleString()}
    `;
    
    const mailtoLink = `mailto:help@myforeclosuresolution.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    window.location.href = mailtoLink;
}

function handleLeadMagnetSubmission(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Show loading state
    const submitButton = form.querySelector('.lead-magnet-button');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Sending Checklist...';
    submitButton.disabled = true;
    
    // Facebook Pixel event
    if (typeof fbq !== 'undefined') {
        fbq('track', 'Lead');
    }
    
    // Google Analytics event
    if (typeof gtag !== 'undefined') {
        gtag('event', 'generate_lead', {
            'event_category': 'lead_magnet',
            'event_label': 'foreclosure_checklist'
        });
    }
    
    // Submit to Google Sheets (same endpoint as contact form)
    submitToGoogleSheets({
        ...data,
        type: 'lead_magnet',
        lead_magnet: 'California Foreclosure Timeline Checklist'
    })
        .then(() => {
            // Redirect to download page
            window.location.href = 'checklist-download.html';
        })
        .catch(error => {
            console.error('Lead magnet submission error:', error);
            alert('There was an error sending your checklist. Please text us at (949) 565-5285 for immediate assistance.');
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        });
}

// Exit Intent Popup Functions
let exitIntentShown = false;
let mouseLeftWindow = false;

function initExitIntent() {
    // Show on all devices
    
    // Don't show if user already converted
    if (localStorage.getItem('exitIntentShown') === 'true') return;
    
    // Track mouse movement
    document.addEventListener('mouseleave', function(e) {
        // Check if mouse left through the top of the window
        if (e.clientY <= 0 && !exitIntentShown) {
            showExitPopup();
        }
    });
    
    // Also trigger on scroll up near top (mobile behavior)
    let lastScrollY = window.scrollY;
    window.addEventListener('scroll', function() {
        if (window.scrollY < lastScrollY && window.scrollY < 100 && !exitIntentShown) {
            // User scrolled up near top of page
            setTimeout(() => {
                if (!exitIntentShown) showExitPopup();
            }, 1000);
        }
        lastScrollY = window.scrollY;
    });
    
    // Fallback: Show after 15 seconds if no other trigger (for easier testing)
    setTimeout(() => {
        if (!exitIntentShown && !hasUserEngaged()) {
            showExitPopup();
        }
    }, 15000);
    
    // Debug trigger for testing - remove in production
    window.testExitPopup = function() {
        showExitPopup();
    };
}

function hasUserEngaged() {
    // Check if user has scrolled significantly, filled form, or clicked CTA
    return window.scrollY > (window.innerHeight * 0.5) || 
           document.querySelector('input:focus') !== null ||
           localStorage.getItem('userEngaged') === 'true';
}

function showExitPopup() {
    if (exitIntentShown) return;
    
    exitIntentShown = true;
    const popup = document.getElementById('exit-intent-popup');
    if (popup) {
        popup.style.display = 'flex';
        
        // Track popup shown event
        if (typeof gtag !== 'undefined') {
            gtag('event', 'exit_intent_shown', {
                'event_category': 'popup',
                'event_label': 'foreclosure_checklist'
            });
        }
        
        // Focus first input
        setTimeout(() => {
            const firstInput = popup.querySelector('input[type="text"]');
            if (firstInput) firstInput.focus();
        }, 500);
    }
}

function closeExitPopup() {
    const popup = document.getElementById('exit-intent-popup');
    if (popup) {
        popup.style.display = 'none';
        localStorage.setItem('exitIntentShown', 'true');
        
        // Track popup closed event
        if (typeof gtag !== 'undefined') {
            gtag('event', 'exit_intent_closed', {
                'event_category': 'popup',
                'event_label': 'foreclosure_checklist'
            });
        }
    }
}

function handleExitPopupSubmission(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Handle multiple checkbox values for situation
    const situationCheckboxes = form.querySelectorAll('input[name="situation"]:checked');
    const selectedSituations = Array.from(situationCheckboxes).map(cb => cb.value);
    data.situation = selectedSituations.join(', ');
    
    // Show loading state
    const submitButton = form.querySelector('.exit-popup-button');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Sending Checklist...';
    submitButton.disabled = true;
    
    // Facebook Pixel event
    if (typeof fbq !== 'undefined') {
        fbq('track', 'Lead');
    }
    
    // Google Analytics event
    if (typeof gtag !== 'undefined') {
        gtag('event', 'generate_lead', {
            'event_category': 'exit_intent_popup',
            'event_label': 'foreclosure_checklist'
        });
    }
    
    // Submit to Google Sheets
    submitToGoogleSheets({
        ...data,
        type: 'exit_intent_popup',
        lead_magnet: 'California Foreclosure Timeline Checklist'
    })
        .then(() => {
            // Close popup and redirect to download page
            closeExitPopup();
            window.location.href = 'checklist-download.html';
        })
        .catch(error => {
            console.error('Exit popup submission error:', error);
            alert('There was an error sending your checklist. Please text us at (949) 565-5285 for immediate assistance.');
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        });
}

// Close popup when clicking outside
document.addEventListener('click', function(e) {
    const popup = document.getElementById('exit-intent-popup');
    if (popup && e.target === popup) {
        closeExitPopup();
    }
});

// Close popup with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeExitPopup();
        closeEmergencyPopup();
    }
});

// Emergency Button Click Handler
function handleEmergencyButtonClick() {
    // Show emergency popup after a delay to provide fallback option
    setTimeout(() => {
        showEmergencyPopup();
    }, 3000); // Show popup after 3 seconds as fallback
}

// Emergency Contact Functions
function showEmergencyPopup() {
    const popup = document.getElementById('emergency-contact-popup');
    if (popup) {
        popup.style.display = 'flex';
        
        // Track popup shown event
        if (typeof gtag !== 'undefined') {
            gtag('event', 'emergency_popup_shown', {
                'event_category': 'urgent_lead',
                'event_label': 'emergency_contact'
            });
        }
        
        // Focus first input
        setTimeout(() => {
            const firstInput = popup.querySelector('input[type="text"]');
            if (firstInput) firstInput.focus();
        }, 500);
    }
}

function closeEmergencyPopup() {
    const popup = document.getElementById('emergency-contact-popup');
    if (popup) {
        popup.style.display = 'none';
        
        // Track popup closed event
        if (typeof gtag !== 'undefined') {
            gtag('event', 'emergency_popup_closed', {
                'event_category': 'urgent_lead',
                'event_label': 'emergency_contact'
            });
        }
    }
}

function handleEmergencyContactSubmission(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Handle multiple checkbox values for situation
    const situationCheckboxes = form.querySelectorAll('input[name="situation"]:checked');
    const selectedSituations = Array.from(situationCheckboxes).map(cb => cb.value);
    data.situation = selectedSituations.join(', ');
    
    // Show loading state
    const submitButton = form.querySelector('.exit-popup-button');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Submitting Emergency Request...';
    submitButton.disabled = true;
    
    // Facebook Pixel event
    if (typeof fbq !== 'undefined') {
        fbq('track', 'Lead');
    }
    
    // Google Analytics event
    if (typeof gtag !== 'undefined') {
        gtag('event', 'generate_lead', {
            'event_category': 'urgent_lead',
            'event_label': 'emergency_contact_form'
        });
    }
    
    // Submit to Google Sheets with emergency flag
    submitToGoogleSheets({
        ...data,
        type: 'emergency_help',
        timeline: 'immediate',
        foreclosure_status: 'yes'
    })
        .then(() => {
            // Close popup and show success message
            closeEmergencyPopup();
            alert('Emergency request submitted! We will call you within 2 hours during business hours. For immediate assistance, call or text (949) 565-5285.');
        })
        .catch(error => {
            console.error('Emergency form submission error:', error);
            alert('There was an error submitting your emergency request. Please call us immediately at (949) 565-5285.');
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        });
}

// Close emergency popup when clicking outside
document.addEventListener('click', function(e) {
    const emergencyPopup = document.getElementById('emergency-contact-popup');
    if (emergencyPopup && e.target === emergencyPopup) {
        closeEmergencyPopup();
    }
});

// Advanced System Integration Functions
function submitToAdvancedSystem(data) {
    // Submit to advanced lead capture API
    return fetch('/api/lead-capture', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    });
}

function determineUrgencyLevel(data) {
    // Analyze form data to determine urgency
    const urgentIndicators = [
        'auction',
        'notice of sale',
        'foreclosure',
        'emergency',
        'urgent',
        'immediate',
        'less than 30 days',
        'notice of default'
    ];
    
    const situation = (data.situation || '').toLowerCase();
    const address = (data.address || '').toLowerCase();
    const name = (data.name || '').toLowerCase();
    
    const allText = [situation, address, name].join(' ');
    
    // Check for emergency indicators
    if (urgentIndicators.some(indicator => allText.includes(indicator))) {
        if (allText.includes('auction') || allText.includes('sale')) {
            return 'emergency';
        }
        return 'urgent';
    }
    
    // Default urgency levels
    if (data.form_type === 'emergency') return 'emergency';
    if (data.form_type === 'consultation') return 'concerned';
    
    return 'exploring';
}

function getSessionTrackingData() {
    // Gather session data for lead scoring
    return {
        sessionId: getSessionId(),
        timeOnSite: Date.now() - (sessionData?.startTime || Date.now()),
        pageViews: sessionData?.pageViews || 1,
        scrollDepth: sessionData?.engagement?.scrollDepth || 0,
        formInteractions: sessionData?.engagement?.formInteractions || 0,
        phoneClicks: sessionData?.engagement?.phoneClicks || 0,
        consultationInterest: sessionData?.engagement?.consultationInterest || false,
        leadScore: sessionStorage.getItem('leadScore') || 0
    };
}

function getTrafficSource() {
    const referrer = document.referrer;
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('utm_source')) {
        return urlParams.get('utm_source');
    }
    
    if (referrer.includes('google.com/maps') || referrer.includes('business.google.com')) {
        return 'google_my_business';
    }
    if (referrer.includes('google.com')) return 'google_organic';
    if (referrer.includes('facebook.com')) return 'facebook';
    if (referrer.includes('linkedin.com')) return 'linkedin';
    if (referrer && !referrer.includes(window.location.hostname)) return 'referral';
    if (!referrer) return 'direct';
    
    return 'unknown';
}

function getDeviceType() {
    const width = window.innerWidth;
    if (width <= 768) return 'mobile';
    if (width <= 1024) return 'tablet';
    return 'desktop';
}

function getSessionId() {
    let sessionId = sessionStorage.getItem('sessionId');
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        sessionStorage.setItem('sessionId', sessionId);
    }
    return sessionId;
}

// Real-time lead qualification popup
function showLeadQualificationPopup(score) {
    if (score < 75) return; // Only show for warm/hot leads
    
    const popup = document.createElement('div');
    popup.id = 'lead-qualification-popup';
    popup.style.cssText = `
        position: fixed; bottom: 20px; right: 20px; background: #059669; 
        color: white; padding: 20px; border-radius: 10px; max-width: 350px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.3); z-index: 9999;
        animation: slideInRight 0.5s ease-out;
    `;
    
    popup.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
            <div>
                <h4 style="margin: 0 0 5px 0; font-size: 16px;">🎯 Priority Status Unlocked</h4>
                <p style="margin: 0; font-size: 14px; opacity: 0.9;">Your engagement qualifies you for priority assistance</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: none; border: none; color: white; font-size: 20px; cursor: pointer; padding: 0; line-height: 1;">×</button>
        </div>
        <div style="text-align: center; margin-top: 15px;">
            <a href="virtual-consultation.html?priority=true" 
               onclick="gtag('event', 'priority_qualification_click', {'event_category': 'hot_lead'});"
               style="background: white; color: #059669; padding: 10px 20px; border-radius: 5px; 
                      text-decoration: none; font-weight: 600; font-size: 14px; display: inline-block;">
                📅 Book Priority Consultation
            </a>
        </div>
    `;
    
    // Add animation CSS
    if (!document.getElementById('popup-animations')) {
        const style = document.createElement('style');
        style.id = 'popup-animations';
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(popup);
    
    // Auto-remove after 15 seconds
    setTimeout(() => {
        if (document.getElementById('lead-qualification-popup')) {
            popup.remove();
        }
    }, 15000);
}

// Enhanced form handling for emergency forms
function handleEmergencyContactSubmission(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Handle multiple checkbox values for situation
    const situationCheckboxes = form.querySelectorAll('input[name="situation"]:checked');
    const selectedSituations = Array.from(situationCheckboxes).map(cb => cb.value);
    data.situation = selectedSituations.join(', ');
    
    // Mark as emergency
    data.form_type = 'emergency';
    data.urgency_level = 'emergency';
    data.session_data = getSessionTrackingData();
    data.lead_source = getTrafficSource();
    data.device_type = getDeviceType();
    
    // Show loading state
    const submitButton = form.querySelector('.exit-popup-button');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Submitting Emergency Request...';
    submitButton.disabled = true;
    
    // Track emergency form completion
    if (typeof gtag !== 'undefined') {
        gtag('event', 'emergency_form_completion', {
            'event_category': 'Emergency Lead',
            'event_label': 'emergency_contact_form',
            'value': 100
        });
    }
    
    // Update lead score
    if (typeof updateLeadScore === 'function') {
        updateLeadScore('emergency_form', {
            formType: 'emergency',
            urgency: 'emergency',
            value: 100
        });
    }
    
    // Submit to advanced system with high priority
    submitToAdvancedSystem(data)
        .then(response => {
            closeEmergencyPopup();
            
            // Show priority response message
            alert(`Emergency request submitted! Score: ${response.score}. We will call you within 1 hour during business hours. For immediate assistance, call or text (949) 565-5285.`);
            
            // Track conversion
            if (typeof fbq !== 'undefined') {
                fbq('track', 'Lead', {
                    content_name: 'Emergency Foreclosure Help',
                    content_category: 'Emergency Lead',
                    value: response.score || 100
                });
            }
        })
        .catch(error => {
            console.error('Emergency form submission error:', error);
            
            // Fallback to basic submission
            submitToGoogleSheets({
                ...data,
                type: 'emergency_help',
                timeline: 'immediate',
                foreclosure_status: 'yes'
            })
            .then(() => {
                closeEmergencyPopup();
                alert('Emergency request submitted! We will call you within 2 hours during business hours. For immediate assistance, call or text (949) 565-5285.');
            })
            .catch(() => {
                alert('There was an error submitting your emergency request. Please call us immediately at (949) 565-5285.');
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            });
        });
}

// Monitor and trigger popups based on lead score
if (typeof sessionStorage !== 'undefined') {
    setInterval(() => {
        const currentScore = parseInt(sessionStorage.getItem('leadScore') || '0');
        
        // Show qualification popup for scores 75+
        if (currentScore >= 75 && !sessionStorage.getItem('qualificationPopupShown')) {
            sessionStorage.setItem('qualificationPopupShown', 'true');
            setTimeout(() => showLeadQualificationPopup(currentScore), 2000);
        }
    }, 10000); // Check every 10 seconds
}