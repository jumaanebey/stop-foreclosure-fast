// Form handling and analytics
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contact-form');
    const leadMagnetForm = document.getElementById('lead-magnet-form');
    const exitPopupForm = document.getElementById('exit-popup-form');
    
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
    
    // Show loading state
    const submitButton = form.querySelector('.submit-button');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Submitting...';
    submitButton.disabled = true;
    
    // Facebook Pixel event
    if (typeof fbq !== 'undefined') {
        fbq('track', 'Lead');
    }
    
    // Google Analytics event
    if (typeof gtag !== 'undefined') {
        gtag('event', 'generate_lead', {
            'event_category': 'engagement',
            'event_label': 'contact_form'
        });
    }
    
    // Submit to Google Sheets (you'll need to replace with your Web App URL)
    submitToGoogleSheets(data)
        .then(() => {
            window.location.href = 'thank-you.html';
        })
        .catch(error => {
            console.error('Form submission error:', error);
            alert('There was an error submitting your form. Please text us at (949) 328-4811 for immediate assistance.');
            submitButton.textContent = originalText;
            submitButton.disabled = false;
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
            alert('There was an error sending your checklist. Please text us at (949) 328-4811 for immediate assistance.');
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        });
}

// Exit Intent Popup Functions
let exitIntentShown = false;
let mouseLeftWindow = false;

function initExitIntent() {
    // Only show on desktop (not mobile)
    if (window.innerWidth < 768) return;
    
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
    
    // Fallback: Show after 30 seconds if no other trigger
    setTimeout(() => {
        if (!exitIntentShown && !hasUserEngaged()) {
            showExitPopup();
        }
    }, 30000);
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
            alert('There was an error sending your checklist. Please text us at (949) 328-4811 for immediate assistance.');
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
    }
});