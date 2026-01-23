// Advanced Lead Capture & CRM Integration API
// SECURITY HARDENED VERSION - Rate limiting, input validation, CORS restrictions

const express = require('express');
const cors = require('cors');
const nodemailer = require('nodemailer');
const app = express();

// ============ SECURITY: CORS Configuration ============
const allowedOrigins = [
    'https://myforeclosuresolution.com',
    'https://www.myforeclosuresolution.com',
    process.env.NODE_ENV === 'development' ? 'http://localhost:3000' : null
].filter(Boolean);

app.use(cors({
    origin: function(origin, callback) {
        // Allow requests with no origin (mobile apps, curl, etc) in dev only
        if (!origin && process.env.NODE_ENV === 'development') {
            return callback(null, true);
        }
        if (allowedOrigins.includes(origin)) {
            return callback(null, true);
        }
        callback(new Error('CORS not allowed'));
    },
    credentials: true,
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json({ limit: '10kb' })); // Limit body size

// ============ SECURITY: Rate Limiting ============
const rateLimitStore = new Map();

function rateLimit(windowMs = 60000, maxRequests = 5) {
    return (req, res, next) => {
        const ip = req.ip || req.connection.remoteAddress || 'unknown';
        const now = Date.now();
        const key = `${ip}`;

        if (!rateLimitStore.has(key)) {
            rateLimitStore.set(key, []);
        }

        const requests = rateLimitStore.get(key);
        const validRequests = requests.filter(time => now - time < windowMs);

        if (validRequests.length >= maxRequests) {
            return res.status(429).json({
                success: false,
                error: 'Too many requests. Please try again later.',
                retryAfter: Math.ceil((validRequests[0] + windowMs - now) / 1000)
            });
        }

        validRequests.push(now);
        rateLimitStore.set(key, validRequests);
        next();
    };
}

// Clean up old rate limit entries every 5 minutes
setInterval(() => {
    const now = Date.now();
    for (const [key, requests] of rateLimitStore.entries()) {
        const validRequests = requests.filter(time => now - time < 300000);
        if (validRequests.length === 0) {
            rateLimitStore.delete(key);
        } else {
            rateLimitStore.set(key, validRequests);
        }
    }
}, 300000);

// ============ SECURITY: Input Validation & Sanitization ============
function sanitizeString(str, maxLength = 200) {
    if (typeof str !== 'string') return '';
    return str
        .trim()
        .slice(0, maxLength)
        .replace(/[<>]/g, '') // Remove potential HTML tags
        .replace(/javascript:/gi, '') // Remove javascript: protocol
        .replace(/on\w+=/gi, ''); // Remove event handlers
}

function escapeHtml(str) {
    if (typeof str !== 'string') return '';
    const htmlEntities = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    };
    return str.replace(/[&<>"']/g, char => htmlEntities[char]);
}

function validateEmail(email) {
    if (typeof email !== 'string') return false;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email) && email.length <= 254;
}

function validatePhone(phone) {
    if (typeof phone !== 'string') return false;
    const cleaned = phone.replace(/[\s\-\(\)\.]/g, '');
    return /^[\+]?[0-9]{10,15}$/.test(cleaned);
}

function validateLeadData(data) {
    const errors = [];

    if (!data || typeof data !== 'object') {
        return { valid: false, errors: ['Invalid request body'] };
    }

    // Required field validation
    if (!data.email || !validateEmail(data.email)) {
        errors.push('Valid email is required');
    }

    if (data.phone && !validatePhone(data.phone)) {
        errors.push('Invalid phone number format');
    }

    if (data.name && typeof data.name === 'string' && data.name.length > 100) {
        errors.push('Name is too long (max 100 characters)');
    }

    if (data.property_address && typeof data.property_address === 'string' && data.property_address.length > 300) {
        errors.push('Address is too long (max 300 characters)');
    }

    // Check for suspicious patterns (potential XSS/injection)
    const suspiciousPatterns = [/<script/i, /javascript:/i, /on\w+\s*=/i, /<iframe/i, /eval\s*\(/i];
    const fieldsToCheck = ['name', 'email', 'phone', 'property_address', 'situation', 'message'];

    for (const field of fieldsToCheck) {
        if (data[field] && typeof data[field] === 'string') {
            for (const pattern of suspiciousPatterns) {
                if (pattern.test(data[field])) {
                    errors.push(`Suspicious content detected in ${field}`);
                    break;
                }
            }
        }
    }

    return { valid: errors.length === 0, errors };
}

// Email configuration (use environment variables in production)
const emailTransporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: process.env.EMAIL_USER || 'help@myforeclosuresolution.com',
        pass: process.env.EMAIL_PASSWORD || 'your-app-password'
    }
});

// Lead scoring function
function calculateLeadScore(leadData) {
    let score = 0;

    // Urgency scoring (highest priority)
    const urgencyScores = {
        'emergency': 100,
        'urgent': 75,
        'concerned': 50,
        'exploring': 25
    };
    score += urgencyScores[leadData.urgency_level] || 0;

    // Situation scoring
    if (leadData.situation) {
        const situation = String(leadData.situation);
        if (situation.includes('auction_scheduled')) score += 80;
        if (situation.includes('received_notice_of_default')) score += 60;
        if (situation.includes('missed_payments')) score += 40;
        if (situation.includes('less_than_30_days')) score += 70;
    }

    // Contact completeness
    if (leadData.phone) score += 20;
    if (leadData.email) score += 15;
    if (leadData.property_address) score += 15;

    // Form type
    if (leadData.form_type === 'emergency') score += 50;
    if (leadData.form_type === 'consultation') score += 40;
    if (leadData.form_type === 'lead_magnet') score += 25;

    return Math.min(score, 300);
}

// Determine priority level
function determinePriority(score) {
    if (score >= 200) return 'P1';
    if (score >= 150) return 'P2';
    if (score >= 100) return 'P3';
    return 'P4';
}

// Send to CRM (example with webhook)
async function sendToCRM(leadData, score, priority) {
    const crmData = {
        source: 'website_form',
        lead_data: {
            name: sanitizeString(leadData.name, 100),
            email: sanitizeString(leadData.email, 254),
            phone: sanitizeString(leadData.phone, 20),
            property_address: sanitizeString(leadData.property_address, 300),
            situation: sanitizeString(leadData.situation, 500),
            urgency_level: sanitizeString(leadData.urgency_level, 20),
            form_type: sanitizeString(leadData.form_type, 50),
            lead_score: score,
            priority: priority,
            timestamp: new Date().toISOString(),
            estimated_property_value: await estimatePropertyValue(leadData.property_address),
            county: extractCountyFromAddress(leadData.property_address),
            followup_sequence: determineEmailSequence(leadData, score)
        },
        auto_assign: true
    };

    try {
        const webhookUrl = process.env.CRM_WEBHOOK_URL;
        if (!webhookUrl || webhookUrl === 'https://hooks.zapier.com/hooks/catch/your-webhook') {
            console.log('CRM webhook not configured, skipping...');
            return;
        }

        const response = await fetch(webhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${process.env.CRM_API_KEY}`
            },
            body: JSON.stringify(crmData)
        });

        if (response.ok) {
            console.log('Lead sent to CRM successfully');
            return await response.json();
        } else {
            console.error('Failed to send to CRM:', response.statusText);
        }
    } catch (error) {
        console.error('CRM integration error:', error);
    }
}

// Trigger automated email sequence
async function triggerEmailSequence(leadData, score) {
    const sequence = determineEmailSequence(leadData, score);
    const welcomeEmailTemplate = getWelcomeEmailTemplate(leadData, sequence);

    try {
        await emailTransporter.sendMail({
            from: '"My Foreclosure Solution" <help@myforeclosuresolution.com>',
            to: sanitizeString(leadData.email, 254),
            subject: welcomeEmailTemplate.subject,
            html: welcomeEmailTemplate.html
        });

        console.log('Welcome email sent successfully');
        scheduleFollowUpEmails(leadData, sequence);

    } catch (error) {
        console.error('Email sending error:', error);
    }
}

function determineEmailSequence(leadData, score) {
    if (score >= 200) return 'emergency_sequence';
    if (score >= 150) return 'urgent_sequence';
    if (score >= 100) return 'standard_sequence';
    return 'nurture_sequence';
}

function getWelcomeEmailTemplate(leadData, sequence) {
    // SECURITY: Escape user input before inserting into HTML
    const safeName = escapeHtml(sanitizeString(leadData.name, 100)) || 'there';

    const templates = {
        emergency_sequence: {
            subject: 'URGENT: Emergency Foreclosure Help Available - Response Within 1 Hour',
            html: `
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: #dc2626; color: white; padding: 20px; text-align: center;">
                        <h1>EMERGENCY RESPONSE ACTIVATED</h1>
                    </div>
                    <div style="padding: 30px 20px;">
                        <h2>Hi ${safeName},</h2>
                        <p><strong>Your emergency foreclosure request has been received and prioritized.</strong></p>

                        <div style="background: #fef2f2; padding: 20px; border-left: 4px solid #dc2626; margin: 20px 0;">
                            <h3 style="color: #dc2626;">IMMEDIATE ACTIONS:</h3>
                            <ul>
                                <li>Your case assigned to senior foreclosure specialist</li>
                                <li>Response guaranteed within 1 hour during business hours</li>
                                <li>Emergency virtual consultation available TODAY</li>
                                <li>Direct line: <a href="tel:+1-949-565-5285" style="color: #dc2626; font-weight: bold;">(949) 565-5285</a></li>
                            </ul>
                        </div>

                        <p><strong>Licensed California professionals (DRE #02076038 | NMLS #2033637) standing by.</strong></p>

                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://myforeclosuresolution.com/virtual-consultation.html?priority=emergency"
                               style="background: #dc2626; color: white; padding: 15px 30px; text-decoration: none;
                                      border-radius: 8px; font-weight: bold; display: inline-block;">
                                Book Emergency Virtual Consultation
                            </a>
                        </div>

                        <p>Stay strong,<br>
                        Emergency Response Team<br>
                        My Foreclosure Solution</p>
                    </div>
                </div>
            `
        },
        urgent_sequence: {
            subject: 'Priority Foreclosure Help - Virtual Consultation Within 4 Hours',
            html: `
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: #f59e0b; color: white; padding: 20px; text-align: center;">
                        <h1>PRIORITY ASSISTANCE</h1>
                    </div>
                    <div style="padding: 30px 20px;">
                        <h2>Hi ${safeName},</h2>
                        <p>Your foreclosure situation has been marked as <strong>PRIORITY</strong> and assigned to our experienced team.</p>

                        <div style="background: #fef3c7; padding: 20px; border-left: 4px solid #f59e0b; margin: 20px 0;">
                            <h3 style="color: #92400e;">PRIORITY RESPONSE:</h3>
                            <ul>
                                <li>Response within 4 hours during business hours</li>
                                <li>Same-day virtual consultation available</li>
                                <li>Licensed CA professionals (DRE #02076038 | NMLS #2033637)</li>
                                <li>Emergency line: <a href="tel:+1-949-565-5285" style="color: #92400e; font-weight: bold;">(949) 565-5285</a></li>
                            </ul>
                        </div>

                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://myforeclosuresolution.com/virtual-consultation.html?priority=urgent"
                               style="background: #f59e0b; color: white; padding: 15px 30px; text-decoration: none;
                                      border-radius: 8px; font-weight: bold; display: inline-block;">
                                Schedule Priority Virtual Consultation
                            </a>
                        </div>
                    </div>
                </div>
            `
        },
        standard_sequence: {
            subject: 'Your California Foreclosure Resources are Ready',
            html: `
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; padding: 30px 20px; text-align: center;">
                        <h1>My Foreclosure Solution</h1>
                        <p>California's Virtual Foreclosure Specialists</p>
                    </div>
                    <div style="padding: 30px 20px;">
                        <h2 style="color: #1e40af;">Your California Foreclosure Resources are Ready</h2>

                        <p>Hi <strong>${safeName}</strong>,</p>

                        <p>Welcome! Thank you for requesting information about foreclosure help in California.</p>

                        <div style="background: #f8f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #059669;">
                            <h3 style="color: #059669;">INSTANT ACCESS:</h3>
                            <ul>
                                <li><a href="https://myforeclosuresolution.com/downloads/california-foreclosure-timeline-checklist.pdf" style="color: #1e40af;">California Foreclosure Timeline Checklist (PDF)</a></li>
                                <li><a href="https://myforeclosuresolution.com/downloads/emergency-action-steps.pdf" style="color: #1e40af;">Emergency Action Steps Guide</a></li>
                                <li><a href="https://myforeclosuresolution.com/downloads/virtual-consultation-prep.pdf" style="color: #1e40af;">Virtual Consultation Preparation Checklist</a></li>
                                <li><strong>Direct line:</strong> <a href="tel:+1-949-565-5285" style="color: #dc2626; font-weight: bold;">(949) 565-5285</a></li>
                            </ul>
                        </div>

                        <p><strong>Licensed California real estate professionals (DRE #02076038 | NMLS #2033637)</strong> serving all 58 counties virtually.</p>

                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://myforeclosuresolution.com/virtual-consultation.html"
                               style="background: #059669; color: white; padding: 15px 30px; text-decoration: none;
                                      border-radius: 8px; font-weight: bold; display: inline-block;">
                                Book Free Virtual Consultation
                            </a>
                        </div>
                    </div>
                </div>
            `
        }
    };

    return templates[sequence] || templates.standard_sequence;
}

function scheduleFollowUpEmails(leadData, sequence) {
    console.log(`Scheduling ${sequence} follow-up emails for ${sanitizeString(leadData.email)}`);
}

async function estimatePropertyValue(address) {
    if (!address) return null;
    return 500000; // Placeholder
}

function extractCountyFromAddress(address) {
    if (!address || typeof address !== 'string') return 'Unknown';

    const counties = ['Los Angeles', 'Orange', 'San Diego', 'Riverside', 'San Bernardino'];
    for (const county of counties) {
        if (address.toLowerCase().includes(county.toLowerCase())) {
            return county;
        }
    }
    return 'Unknown';
}

// ============ MAIN ENDPOINT WITH SECURITY ============
app.post('/api/lead-capture', rateLimit(60000, 5), async (req, res) => {
    try {
        // Validate input
        const validation = validateLeadData(req.body);
        if (!validation.valid) {
            return res.status(400).json({
                success: false,
                errors: validation.errors
            });
        }

        const leadData = req.body;

        // Calculate lead score
        const score = calculateLeadScore(leadData);
        const priority = determinePriority(score);

        // Send to CRM
        await sendToCRM(leadData, score, priority);

        // Trigger email sequence
        if (leadData.email && validateEmail(leadData.email)) {
            await triggerEmailSequence(leadData, score);
        }

        // Send immediate notification for high-priority leads
        if (priority === 'P1' || priority === 'P2') {
            await sendImmediateNotification(leadData, score);
        }

        res.json({
            success: true,
            lead_id: `lead_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            score: score,
            priority: priority,
            next_steps: getNextSteps(priority)
        });

    } catch (error) {
        console.error('Lead capture error:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to process lead'
        });
    }
});

// Send immediate notification for high-priority leads
async function sendImmediateNotification(leadData, score) {
    // SECURITY: Escape all user input
    const safeName = escapeHtml(sanitizeString(leadData.name, 100));
    const safeEmail = escapeHtml(sanitizeString(leadData.email, 254));
    const safePhone = escapeHtml(sanitizeString(leadData.phone, 20));
    const safeSituation = escapeHtml(sanitizeString(leadData.situation, 500));
    const safeAddress = escapeHtml(sanitizeString(leadData.property_address, 300));

    const notificationEmail = {
        from: '"Lead Alert System" <alerts@myforeclosuresolution.com>',
        to: 'help@myforeclosuresolution.com',
        subject: `HIGH PRIORITY LEAD - Score: ${score}`,
        html: `
            <h2>High Priority Lead Alert</h2>
            <p><strong>Score:</strong> ${score}</p>
            <p><strong>Name:</strong> ${safeName}</p>
            <p><strong>Email:</strong> ${safeEmail}</p>
            <p><strong>Phone:</strong> ${safePhone}</p>
            <p><strong>Situation:</strong> ${safeSituation}</p>
            <p><strong>Property:</strong> ${safeAddress}</p>
            <p><strong>Timestamp:</strong> ${new Date().toISOString()}</p>
            <p><strong>Response Required:</strong> Within 1-4 hours</p>
        `
    };

    await emailTransporter.sendMail(notificationEmail);
}

function getNextSteps(priority) {
    const steps = {
        'P1': ['Immediate call within 1 hour', 'Same-day virtual consultation', 'Emergency response protocol'],
        'P2': ['Priority call within 4 hours', 'Next-day consultation available', 'Urgent follow-up sequence'],
        'P3': ['Call within 24 hours', 'Standard consultation booking', 'Regular follow-up sequence'],
        'P4': ['Contact within 72 hours', 'Nurture sequence initiated', 'Educational content delivery']
    };

    return steps[priority] || steps['P4'];
}

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Lead capture API running on port ${PORT}`);
});

module.exports = app;
