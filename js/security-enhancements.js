/**
 * Security Enhancements for MyForeclosureSolutions.com
 * Implements proper input validation, sanitization, and security measures
 */

// CSRF Protection Token
let csrfToken = null;

// Initialize security measures
document.addEventListener('DOMContentLoaded', function() {
    initializeSecurity();
    addFormValidation();
    implementRateLimiting();
});

/**
 * Initialize security measures
 */
function initializeSecurity() {
    // Generate CSRF token
    csrfToken = generateCSRFToken();
    
    // Add security headers via meta tags
    addSecurityHeaders();
    
    // Validate all external URLs
    validateExternalLinks();
    
    // Initialize session timeout
    initializeSessionTimeout();
}

/**
 * Generate CSRF token
 */
function generateCSRFToken() {
    const array = new Uint32Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}

/**
 * Add security headers
 */
function addSecurityHeaders() {
    // Add CSP via meta tag if not already present
    if (!document.querySelector('meta[http-equiv="Content-Security-Policy"]')) {
        const csp = document.createElement('meta');
        csp.httpEquiv = 'Content-Security-Policy';
        csp.content = "default-src 'self'; " +
                     "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com; " +
                     "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; " +
                     "font-src 'self' https://fonts.gstatic.com; " +
                     "img-src 'self' data: https:; " +
                     "connect-src 'self' https://www.google-analytics.com;";
        document.head.appendChild(csp);
    }
}

/**
 * Enhanced form validation with security checks
 */
function addFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Add CSRF token to all forms
        addCSRFTokenToForm(form);
        
        // Enhanced validation
        form.addEventListener('submit', function(e) {
            if (!validateFormSecurity(form)) {
                e.preventDefault();
                return false;
            }
        });
        
        // Real-time input validation
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                validateInput(input);
            });
        });
    });
}

/**
 * Add CSRF token to form
 */
function addCSRFTokenToForm(form) {
    // Check if CSRF token already exists
    let csrfInput = form.querySelector('input[name="csrf_token"]');
    
    if (!csrfInput) {
        csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);
    }
}

/**
 * Validate form security
 */
function validateFormSecurity(form) {
    const errors = [];
    
    // Check CSRF token
    const csrfInput = form.querySelector('input[name="csrf_token"]');
    if (!csrfInput || csrfInput.value !== csrfToken) {
        errors.push('Security token invalid');
    }
    
    // Validate all inputs
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    inputs.forEach(input => {
        if (!validateInput(input)) {
            errors.push(`Invalid ${input.name || input.type}`);
        }
    });
    
    if (errors.length > 0) {
        console.error('Form validation errors:', errors);
        showSecureMessage('Please correct form errors and try again.');
        return false;
    }
    
    return true;
}

/**
 * Validate individual input
 */
function validateInput(input) {
    const value = input.value.trim();
    const type = input.type;
    const name = input.name;
    
    // Remove any existing error styling
    input.classList.remove('security-error');
    
    let isValid = true;
    
    switch (type) {
        case 'email':
            isValid = validateEmail(value);
            break;
        case 'tel':
            isValid = validatePhone(value);
            break;
        case 'text':
            if (name === 'address' || input.placeholder?.includes('address')) {
                isValid = validateAddress(value);
            } else {
                isValid = validateText(value);
            }
            break;
        case 'textarea':
            isValid = validateText(value);
            break;
    }
    
    // Check for potential injection attempts
    if (isValid && containsSuspiciousContent(value)) {
        isValid = false;
    }
    
    if (!isValid) {
        input.classList.add('security-error');
    }
    
    return isValid;
}

/**
 * Email validation
 */
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email) && email.length <= 254;
}

/**
 * Phone validation
 */
function validatePhone(phone) {
    const phoneRegex = /^[\+]?[\d\s\(\)\-\.]{10,15}$/;
    return phoneRegex.test(phone);
}

/**
 * Address validation
 */
function validateAddress(address) {
    // Basic address validation - not empty, reasonable length, no scripts
    return address.length > 5 && 
           address.length <= 200 && 
           !containsSuspiciousContent(address);
}

/**
 * Text validation
 */
function validateText(text) {
    if (text.length === 0) return true; // Allow empty for optional fields
    return text.length <= 1000 && !containsSuspiciousContent(text);
}

/**
 * Check for suspicious content (potential XSS, injection)
 */
function containsSuspiciousContent(value) {
    const suspiciousPatterns = [
        /<script/i,
        /javascript:/i,
        /on\w+\s*=/i,
        /<iframe/i,
        /<object/i,
        /<embed/i,
        /data:text\/html/i,
        /vbscript:/i,
        /<meta/i,
        /eval\s*\(/i,
        /expression\s*\(/i
    ];
    
    return suspiciousPatterns.some(pattern => pattern.test(value));
}

/**
 * Rate limiting implementation
 */
const rateLimits = new Map();

function implementRateLimiting() {
    // Limit form submissions
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (!checkRateLimit('form_submit', 3, 60000)) { // 3 per minute
            e.preventDefault();
            showSecureMessage('Please wait before submitting another form.');
            return false;
        }
    });
    
    // Limit phone clicks
    document.querySelectorAll('a[href^="tel:"]').forEach(link => {
        link.addEventListener('click', function(e) {
            if (!checkRateLimit('phone_click', 5, 60000)) { // 5 per minute
                e.preventDefault();
                showSecureMessage('Please wait before clicking the phone number again.');
                return false;
            }
        });
    });
}

/**
 * Check rate limit
 */
function checkRateLimit(action, maxRequests, timeWindow) {
    const now = Date.now();
    const key = action;
    
    if (!rateLimits.has(key)) {
        rateLimits.set(key, []);
    }
    
    const requests = rateLimits.get(key);
    
    // Remove old requests outside the time window
    const validRequests = requests.filter(time => now - time < timeWindow);
    
    if (validRequests.length >= maxRequests) {
        return false;
    }
    
    validRequests.push(now);
    rateLimits.set(key, validRequests);
    return true;
}

/**
 * Secure message display (prevents XSS)
 */
function showSecureMessage(message) {
    // Create a secure alert alternative
    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
        position: fixed; top: 20px; right: 20px; z-index: 10000;
        background: #f56565; color: white; padding: 1rem;
        border-radius: 0.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        max-width: 300px; word-wrap: break-word;
    `;
    
    // Use textContent to prevent XSS
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 5000);
}

/**
 * Session timeout management
 */
function initializeSessionTimeout() {
    let sessionTimeout;
    const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes
    
    function resetSessionTimeout() {
        clearTimeout(sessionTimeout);
        sessionTimeout = setTimeout(() => {
            // Clear sensitive data
            sessionStorage.clear();
            localStorage.removeItem('leadScore');
            showSecureMessage('Session expired for security. Please refresh the page.');
        }, SESSION_TIMEOUT);
    }
    
    // Reset timeout on user activity
    ['click', 'keypress', 'scroll', 'mousemove'].forEach(event => {
        document.addEventListener(event, resetSessionTimeout, { passive: true });
    });
    
    // Initialize timeout
    resetSessionTimeout();
}

/**
 * Validate external links
 */
function validateExternalLinks() {
    const externalLinks = document.querySelectorAll('a[href^="http"]');
    externalLinks.forEach(link => {
        // Add security attributes
        link.rel = 'noopener noreferrer';
        
        // Validate URL
        try {
            const url = new URL(link.href);
            // Block suspicious domains
            const suspiciousDomains = ['bit.ly', 'tinyurl.com', 'goo.gl'];
            if (suspiciousDomains.includes(url.hostname)) {
                link.style.display = 'none';
                console.warn('Blocked suspicious link:', link.href);
            }
        } catch (e) {
            console.warn('Invalid URL found:', link.href);
            link.style.display = 'none';
        }
    });
}

/**
 * Enhanced phone number validation for click events
 */
function validatePhoneClick(phoneNumber) {
    // Remove common formatting
    const cleaned = phoneNumber.replace(/[\s\-\(\)\.]/g, '');
    
    // Check if it's a valid US phone number format
    const usPhoneRegex = /^(\+1)?[0-9]{10}$/;
    
    if (!usPhoneRegex.test(cleaned)) {
        showSecureMessage('Invalid phone number format');
        return false;
    }
    
    return true;
}

// Override the existing form submission to use secure methods
if (typeof submitPrequalForm !== 'undefined') {
    const originalSubmitPrequalForm = submitPrequalForm;
    
    submitPrequalForm = function(data) {
        // Add security headers
        data.csrf_token = csrfToken;
        data.timestamp = new Date().toISOString();
        data.user_agent = navigator.userAgent.substring(0, 200); // Truncate for security
        
        // Validate data before submission
        if (!validateFormData(data)) {
            showSecureMessage('Invalid form data. Please check your inputs.');
            return;
        }
        
        // Call original function with validated data
        return originalSubmitPrequalForm(data);
    };
}

/**
 * Validate form data before submission
 */
function validateFormData(data) {
    // Check required fields
    const requiredFields = ['name', 'email', 'phone', 'address'];
    
    for (const field of requiredFields) {
        if (!data[field] || typeof data[field] !== 'string') {
            return false;
        }
        
        if (containsSuspiciousContent(data[field])) {
            return false;
        }
    }
    
    // Validate specific field formats
    if (!validateEmail(data.email)) return false;
    if (!validatePhone(data.phone)) return false;
    if (!validateText(data.name)) return false;
    if (!validateAddress(data.address)) return false;
    
    return true;
}

// Add CSS for security error styling
const securityCSS = `
    .security-error {
        border: 2px solid #f56565 !important;
        background-color: #fed7d7 !important;
    }
    
    .security-error:focus {
        box-shadow: 0 0 0 3px rgba(245, 101, 101, 0.3) !important;
    }
`;

const style = document.createElement('style');
style.textContent = securityCSS;
document.head.appendChild(style);

// Export functions for testing
window.securityEnhancements = {
    validateEmail,
    validatePhone,
    validateText,
    validateAddress,
    containsSuspiciousContent,
    checkRateLimit
};