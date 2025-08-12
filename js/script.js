// Form handling and analytics
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmission(this);
        });
    }
    
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
            alert('There was an error submitting your form. Please call us directly at (555) STOP-NOW');
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        });
}

function submitToGoogleSheets(data) {
    // Replace with your Google Apps Script Web App URL
    const GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec';
    
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
    
    const mailtoLink = `mailto:help@stopforeclosurefast.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    window.location.href = mailtoLink;
}