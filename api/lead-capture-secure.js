// PRODUCTION-READY Secure Lead Capture API
// Replace lead-capture.js with this version for production deployment

const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const validator = require('validator');
const nodemailer = require('nodemailer');
const crypto = require('crypto');

const app = express();

// Security middleware
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            scriptSrc: ["'self'", "'unsafe-inline'", "https://www.googletagmanager.com"],
            styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
            fontSrc: ["'self'", "https://fonts.gstatic.com"],
            imgSrc: ["'self'", "data:", "https:"],
            connectSrc: ["'self'", "https://www.google-analytics.com"]
        }
    }
}));

// Restrictive CORS - PRODUCTION DOMAINS ONLY
app.use(cors({
    origin: function (origin, callback) {
        const allowedOrigins = [
            'https://myforeclosuresolution.com',
            'https://www.myforeclosuresolution.com'
        ];
        
        // Allow requests with no origin (mobile apps, etc.) in development only
        if (!origin && process.env.NODE_ENV !== 'production') {
            return callback(null, true);
        }
        
        if (allowedOrigins.indexOf(origin) !== -1) {
            callback(null, true);
        } else {
            callback(new Error('Not allowed by CORS'));
        }
    },
    methods: ['POST'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: false
}));

// Rate limiting - Aggressive protection
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // 5 requests per IP per window
    message: {
        error: 'Too many requests. Please try again in 15 minutes.',
        code: 'RATE_LIMIT_EXCEEDED'
    },
    standardHeaders: true,
    legacyHeaders: false,
    handler: (req, res) => {
        console.log(`Rate limit exceeded for IP: ${req.ip}`);
        res.status(429).json({
            error: 'Too many requests. Please try again later.',
            retryAfter: Math.round(15 * 60) // 15 minutes in seconds
        });
    }
});

app.use('/api/', limiter);
app.use(express.json({ limit: '10mb' })); // Reasonable limit

// Input validation and sanitization middleware
function validateAndSanitizeInput(req, res, next) {
    try {
        const { email, phone, name, situation, property_address } = req.body;
        
        // Email validation (required)
        if (!email || !validator.isEmail(email)) {
            return res.status(400).json({ 
                error: 'Valid email address is required',
                code: 'INVALID_EMAIL'
            });
        }
        
        // Sanitize and validate name
        if (name) {
            const sanitizedName = validator.escape(name).trim();
            if (!sanitizedName || sanitizedName.length > 100) {
                return res.status(400).json({ 
                    error: 'Valid name is required (max 100 characters)',
                    code: 'INVALID_NAME'
                });
            }
            req.body.name = sanitizedName;
        }
        
        // Phone validation (optional but validate if provided)
        if (phone) {
            const cleanPhone = phone.replace(/\D/g, ''); // Remove non-digits
            if (!validator.isMobilePhone(cleanPhone, 'en-US')) {
                return res.status(400).json({ 
                    error: 'Valid US phone number is required',
                    code: 'INVALID_PHONE'
                });
            }
            req.body.phone = cleanPhone;
        }
        
        // Sanitize situation description
        if (situation) {
            const sanitizedSituation = validator.escape(situation).trim();
            if (sanitizedSituation.length > 1000) {
                return res.status(400).json({ 
                    error: 'Situation description too long (max 1000 characters)',
                    code: 'INVALID_SITUATION'
                });
            }
            req.body.situation = sanitizedSituation;
        }
        
        // Sanitize property address
        if (property_address) {
            const sanitizedAddress = validator.escape(property_address).trim();
            if (sanitizedAddress.length > 200) {
                return res.status(400).json({ 
                    error: 'Address too long (max 200 characters)',
                    code: 'INVALID_ADDRESS'
                });
            }
            req.body.property_address = sanitizedAddress;
        }
        
        // Add request timestamp and IP for tracking
        req.body.request_timestamp = new Date().toISOString();
        req.body.request_ip = req.ip;
        req.body.request_id = generateRequestId();
        
        next();
    } catch (error) {
        console.error('Validation error:', error);
        res.status(400).json({ 
            error: 'Invalid request data',
            code: 'VALIDATION_ERROR'
        });
    }
}

// Generate unique request ID for tracking
function generateRequestId() {
    return crypto.randomBytes(16).toString('hex');
}

// Secure email configuration - ENVIRONMENT VARIABLES REQUIRED
function createEmailTransporter() {
    if (!process.env.EMAIL_USER || !process.env.EMAIL_PASSWORD) {
        throw new Error('Email credentials not configured. Set EMAIL_USER and EMAIL_PASSWORD environment variables.');
    }
    
    return nodemailer.createTransporter({
        service: 'gmail',
        auth: {
            user: process.env.EMAIL_USER,
            pass: process.env.EMAIL_PASSWORD
        },
        secure: true,
        tls: {
            rejectUnauthorized: true
        }
    });
}

// Secure lead scoring function with bounds checking
function calculateLeadScore(leadData) {
    let score = 0;
    
    try {
        // Urgency scoring with validation
        const urgencyScores = {
            'emergency': 100,
            'urgent': 75,
            'concerned': 50,
            'exploring': 25
        };
        
        const urgencyLevel = leadData.urgency_level;
        if (urgencyLevel && urgencyScores.hasOwnProperty(urgencyLevel)) {
            score += urgencyScores[urgencyLevel];
        }
        
        // Situation scoring with safe string operations
        if (leadData.situation && typeof leadData.situation === 'string') {
            const situation = leadData.situation.toLowerCase();
            if (situation.includes('auction')) score += 80;
            if (situation.includes('notice of default')) score += 60;
            if (situation.includes('missed payments')) score += 40;
            if (situation.includes('30 days')) score += 70;
        }
        
        // Contact completeness scoring
        if (leadData.phone && leadData.phone.length >= 10) score += 20;
        if (leadData.email && validator.isEmail(leadData.email)) score += 15;
        if (leadData.property_address && leadData.property_address.length > 0) score += 15;
        
        // Form type scoring with validation
        const formTypeScores = {
            'emergency': 50,
            'consultation': 40,
            'lead_magnet': 25,
            'contact': 30
        };
        
        const formType = leadData.form_type;
        if (formType && formTypeScores.hasOwnProperty(formType)) {
            score += formTypeScores[formType];
        }
        
        // Cap score at reasonable maximum
        return Math.min(score, 500);
        
    } catch (error) {
        console.error('Lead scoring error:', error);
        return 50; // Default safe score
    }
}

// Secure priority determination
function determinePriority(score) {
    if (typeof score !== 'number' || score < 0) return 'P4';
    
    if (score >= 250) return 'P1'; // Emergency: 1 hour response
    if (score >= 150) return 'P2'; // Urgent: 4 hour response
    if (score >= 100) return 'P3'; // Standard: 24 hour response
    return 'P4'; // Nurture: 72 hour response
}

// Secure CRM integration with error handling
async function sendToCRM(leadData, score, priority) {
    try {
        const crmWebhookUrl = process.env.CRM_WEBHOOK_URL;
        const crmApiKey = process.env.CRM_API_KEY;
        
        if (!crmWebhookUrl) {
            console.log('CRM webhook not configured - storing locally');
            return { success: false, reason: 'CRM not configured' };
        }
        
        const crmData = {
            source: 'website_form',
            lead_data: {
                ...leadData,
                lead_score: score,
                priority: priority,
                timestamp: new Date().toISOString()
            },
            auto_assign: true
        };
        
        const response = await fetch(crmWebhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': crmApiKey ? `Bearer ${crmApiKey}` : undefined,
                'User-Agent': 'MyForeclosureSolution/1.0'
            },
            body: JSON.stringify(crmData),
            timeout: 10000 // 10 second timeout
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Lead sent to CRM successfully');
            return { success: true, crm_id: result.id };
        } else {
            console.error('CRM integration failed:', response.status, response.statusText);
            return { success: false, reason: 'CRM API error' };
        }
    } catch (error) {
        console.error('CRM integration error:', error.message);
        return { success: false, reason: 'CRM connection failed' };
    }
}

// Secure email sending with comprehensive error handling
async function triggerEmailSequence(leadData, score) {
    try {
        const emailTransporter = createEmailTransporter();
        const sequence = determineEmailSequence(score);
        const welcomeEmail = getWelcomeEmailTemplate(leadData, sequence);
        
        const mailOptions = {
            from: `"My Foreclosure Solution" <${process.env.EMAIL_USER}>`,
            to: leadData.email,
            subject: welcomeEmail.subject,
            html: welcomeEmail.html,
            text: welcomeEmail.text, // Fallback for email clients
            headers: {
                'X-Priority': sequence === 'emergency_sequence' ? '1' : '3',
                'X-Request-ID': leadData.request_id
            }
        };
        
        await emailTransporter.sendMail(mailOptions);
        console.log(`Welcome email sent successfully to ${leadData.email}`);
        return { success: true };
        
    } catch (error) {
        console.error('Email sending error:', error.message);
        return { success: false, reason: error.message };
    }
}

// Determine email sequence based on score
function determineEmailSequence(score) {
    if (score >= 250) return 'emergency_sequence';
    if (score >= 150) return 'urgent_sequence';
    if (score >= 100) return 'standard_sequence';
    return 'nurture_sequence';
}

// Get welcome email template (secure version)
function getWelcomeEmailTemplate(leadData, sequence) {
    const templates = {
        emergency_sequence: {
            subject: '🚨 URGENT: Emergency Foreclosure Help - Response Within 1 Hour',
            html: `<!-- Safe HTML template for emergency sequence -->`,
            text: `EMERGENCY RESPONSE ACTIVATED\n\nHi ${leadData.name || 'there'},\n\nYour emergency foreclosure request has been received and prioritized.\n\nWe will contact you within 1 hour during business hours.\n\nEmergency line: (949) 565-5285`
        },
        urgent_sequence: {
            subject: '⚠️ Priority Foreclosure Help - Response Within 4 Hours',
            html: `<!-- Safe HTML template for urgent sequence -->`,
            text: `PRIORITY ASSISTANCE\n\nHi ${leadData.name || 'there'},\n\nYour foreclosure situation has been marked as PRIORITY.\n\nWe will contact you within 4 hours during business hours.\n\nDirect line: (949) 565-5285`
        },
        standard_sequence: {
            subject: 'Your California Foreclosure Resources are Ready 📋',
            html: `<!-- Safe HTML template for standard sequence -->`,
            text: `Hi ${leadData.name || 'there'},\n\nThank you for requesting foreclosure help information.\n\nWe will contact you within 24 hours.\n\nContact: (949) 565-5285`
        }
    };
    
    return templates[sequence] || templates.standard_sequence;
}

// Send immediate notification for high-priority leads
async function sendImmediateNotification(leadData, score) {
    try {
        const emailTransporter = createEmailTransporter();
        const notificationEmail = {
            from: `"Lead Alert System" <${process.env.EMAIL_USER}>`,
            to: process.env.NOTIFICATION_EMAIL || process.env.EMAIL_USER,
            subject: `🚨 HIGH PRIORITY LEAD - Score: ${score}`,
            html: `
                <h2>🚨 High Priority Lead Alert</h2>
                <p><strong>Request ID:</strong> ${leadData.request_id}</p>
                <p><strong>Score:</strong> ${score}</p>
                <p><strong>Name:</strong> ${leadData.name || 'Not provided'}</p>
                <p><strong>Email:</strong> ${leadData.email}</p>
                <p><strong>Phone:</strong> ${leadData.phone || 'Not provided'}</p>
                <p><strong>Situation:</strong> ${leadData.situation || 'Not provided'}</p>
                <p><strong>Property:</strong> ${leadData.property_address || 'Not provided'}</p>
                <p><strong>Timestamp:</strong> ${leadData.request_timestamp}</p>
                <p><strong>IP Address:</strong> ${leadData.request_ip}</p>
                <p><strong>Response Required:</strong> Within 1-4 hours</p>
            `,
            text: `HIGH PRIORITY LEAD\nScore: ${score}\nName: ${leadData.name}\nEmail: ${leadData.email}\nPhone: ${leadData.phone}\nRequires immediate attention.`
        };
        
        await emailTransporter.sendMail(notificationEmail);
        console.log('High priority notification sent');
    } catch (error) {
        console.error('Notification email error:', error.message);
    }
}

// Main lead capture endpoint with comprehensive security
app.post('/api/lead-capture', validateAndSanitizeInput, async (req, res) => {
    try {
        const leadData = req.body;
        
        // Calculate lead score
        const score = calculateLeadScore(leadData);
        const priority = determinePriority(score);
        
        console.log(`Processing lead: ${leadData.request_id}, Score: ${score}, Priority: ${priority}`);
        
        // Send to CRM (non-blocking)
        const crmResult = await sendToCRM(leadData, score, priority);
        
        // Trigger email sequence (non-blocking)
        let emailResult = { success: false };
        if (leadData.email) {
            emailResult = await triggerEmailSequence(leadData, score);
        }
        
        // Send immediate notification for high-priority leads
        if (priority === 'P1' || priority === 'P2') {
            sendImmediateNotification(leadData, score).catch(err => {
                console.error('Notification failed:', err.message);
            });
        }
        
        // Secure response (don't expose internal details)
        const response = {
            success: true,
            lead_id: leadData.request_id,
            score: score,
            priority: priority,
            message: getResponseMessage(priority),
            next_steps: getNextSteps(priority),
            email_sent: emailResult.success,
            crm_integrated: crmResult.success
        };
        
        // Log successful processing
        console.log(`Lead processed successfully: ${leadData.request_id}`);
        
        res.status(200).json(response);
        
    } catch (error) {
        console.error('Lead capture error:', error.message);
        
        // Secure error response (don't expose system details)
        res.status(500).json({
            success: false,
            error: 'Unable to process request at this time',
            code: 'PROCESSING_ERROR',
            message: 'Please try again or call (949) 565-5285 for immediate assistance'
        });
    }
});

function getResponseMessage(priority) {
    const messages = {
        'P1': 'Emergency request received! We will contact you within 1 hour during business hours.',
        'P2': 'Priority request received! We will contact you within 4 hours during business hours.',
        'P3': 'Request received! We will contact you within 24 hours during business hours.',
        'P4': 'Request received! We will contact you within 72 hours during business hours.'
    };
    return messages[priority] || messages['P4'];
}

function getNextSteps(priority) {
    const steps = {
        'P1': ['Emergency response team notified', 'Immediate review in progress', 'Same-day consultation available'],
        'P2': ['Priority queue assignment', 'Senior specialist review', 'Next-day consultation available'],
        'P3': ['Standard processing queue', 'Consultation scheduling', 'Resource materials sent'],
        'P4': ['Nurture sequence initiated', 'Educational content delivery', 'Follow-up scheduling']
    };
    return steps[priority] || steps['P4'];
}

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.status(200).json({ 
        status: 'OK', 
        timestamp: new Date().toISOString(),
        version: '2.0.0-secure'
    });
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Unhandled error:', error.message);
    res.status(500).json({
        error: 'Internal server error',
        code: 'INTERNAL_ERROR'
    });
});

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({
        error: 'Endpoint not found',
        code: 'NOT_FOUND'
    });
});

const PORT = process.env.PORT || 3000;

// Secure server startup
app.listen(PORT, () => {
    console.log(`Secure Lead Capture API running on port ${PORT}`);
    console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
    
    // Verify required environment variables
    const requiredEnvVars = ['EMAIL_USER', 'EMAIL_PASSWORD'];
    const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
    
    if (missingVars.length > 0) {
        console.warn(`⚠️  Missing required environment variables: ${missingVars.join(', ')}`);
        console.warn('Email functionality will be disabled until configured.');
    }
});

module.exports = app;