// Advanced Lead Capture & CRM Integration API
// This file should be deployed to your server (Node.js/Express, Netlify Functions, or Vercel)

const express = require('express');
const cors = require('cors');
const nodemailer = require('nodemailer');
const app = express();

app.use(cors());
app.use(express.json());

// Email configuration (use environment variables in production)
const emailTransporter = nodemailer.createTransporter({
    service: 'gmail', // or your preferred email service
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
        if (leadData.situation.includes('auction_scheduled')) score += 80;
        if (leadData.situation.includes('received_notice_of_default')) score += 60;
        if (leadData.situation.includes('missed_payments')) score += 40;
        if (leadData.situation.includes('less_than_30_days')) score += 70;
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
    if (score >= 200) return 'P1'; // Response within 1 hour
    if (score >= 150) return 'P2'; // Response within 4 hours
    if (score >= 100) return 'P3'; // Response within 24 hours
    return 'P4'; // Response within 72 hours
}

// Send to CRM (example with webhook - adapt to your CRM)
async function sendToCRM(leadData, score, priority) {
    const crmData = {
        source: 'website_form',
        lead_data: {
            ...leadData,
            lead_score: score,
            priority: priority,
            timestamp: new Date().toISOString(),
            estimated_property_value: await estimatePropertyValue(leadData.property_address),
            county: extractCountyFromAddress(leadData.property_address),
            followup_sequence: determineEmailSequence(leadData, score)
        },
        auto_assign: true
    };
    
    // Send to CRM webhook (replace with your CRM's API endpoint)
    try {
        const response = await fetch(process.env.CRM_WEBHOOK_URL || 'https://hooks.zapier.com/hooks/catch/your-webhook', {
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
    
    // Send immediate welcome email
    const welcomeEmailTemplate = getWelcomeEmailTemplate(leadData, sequence);
    
    try {
        await emailTransporter.sendMail({
            from: '"My Foreclosure Solution" <help@myforeclosuresolution.com>',
            to: leadData.email,
            subject: welcomeEmailTemplate.subject,
            html: welcomeEmailTemplate.html
        });
        
        console.log('Welcome email sent successfully');
        
        // Schedule follow-up emails (you'll need a job queue like Bull or node-cron)
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
    const templates = {
        emergency_sequence: {
            subject: '🚨 URGENT: Emergency Foreclosure Help Available - Response Within 1 Hour',
            html: `
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: #dc2626; color: white; padding: 20px; text-align: center;">
                        <h1>🚨 EMERGENCY RESPONSE ACTIVATED</h1>
                    </div>
                    <div style="padding: 30px 20px;">
                        <h2>Hi ${leadData.name || 'there'},</h2>
                        <p><strong>Your emergency foreclosure request has been received and prioritized.</strong></p>
                        
                        <div style="background: #fef2f2; padding: 20px; border-left: 4px solid #dc2626; margin: 20px 0;">
                            <h3 style="color: #dc2626;">IMMEDIATE ACTIONS:</h3>
                            <ul>
                                <li>✅ Your case assigned to senior foreclosure specialist</li>
                                <li>✅ Response guaranteed within 1 hour during business hours</li>
                                <li>✅ Emergency virtual consultation available TODAY</li>
                                <li>✅ Direct line: <a href="tel:+1-949-565-5285" style="color: #dc2626; font-weight: bold;">(949) 565-5285</a></li>
                            </ul>
                        </div>
                        
                        <p><strong>Licensed California professionals (DRE #02076038 | NMLS #2033637) standing by.</strong></p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://myforeclosuresolution.com/virtual-consultation.html?priority=emergency" 
                               style="background: #dc2626; color: white; padding: 15px 30px; text-decoration: none; 
                                      border-radius: 8px; font-weight: bold; display: inline-block;">
                                📅 Book Emergency Virtual Consultation
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
            subject: '⚠️ Priority Foreclosure Help - Virtual Consultation Within 4 Hours',
            html: `
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: #f59e0b; color: white; padding: 20px; text-align: center;">
                        <h1>⚠️ PRIORITY ASSISTANCE</h1>
                    </div>
                    <div style="padding: 30px 20px;">
                        <h2>Hi ${leadData.name || 'there'},</h2>
                        <p>Your foreclosure situation has been marked as <strong>PRIORITY</strong> and assigned to our experienced team.</p>
                        
                        <div style="background: #fef3c7; padding: 20px; border-left: 4px solid #f59e0b; margin: 20px 0;">
                            <h3 style="color: #92400e;">PRIORITY RESPONSE:</h3>
                            <ul>
                                <li>✅ Response within 4 hours during business hours</li>
                                <li>✅ Same-day virtual consultation available</li>
                                <li>✅ Licensed CA professionals (DRE #02076038 | NMLS #2033637)</li>
                                <li>✅ Emergency line: <a href="tel:+1-949-565-5285" style="color: #92400e; font-weight: bold;">(949) 565-5285</a></li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://myforeclosuresolution.com/virtual-consultation.html?priority=urgent" 
                               style="background: #f59e0b; color: white; padding: 15px 30px; text-decoration: none; 
                                      border-radius: 8px; font-weight: bold; display: inline-block;">
                                📅 Schedule Priority Virtual Consultation
                            </a>
                        </div>
                    </div>
                </div>
            `
        },
        standard_sequence: {
            subject: 'Your California Foreclosure Resources are Ready 📋',
            html: `
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; padding: 30px 20px; text-align: center;">
                        <h1>My Foreclosure Solution</h1>
                        <p>California's Virtual Foreclosure Specialists</p>
                    </div>
                    <div style="padding: 30px 20px;">
                        <h2 style="color: #1e40af;">Your California Foreclosure Resources are Ready 📋</h2>
                        
                        <p>Hi <strong>${leadData.name || 'there'}</strong>,</p>
                        
                        <p>Welcome! Thank you for requesting information about foreclosure help in California.</p>
                        
                        <div style="background: #f8f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #059669;">
                            <h3 style="color: #059669;">🔗 INSTANT ACCESS:</h3>
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
                                📅 Book Free Virtual Consultation
                            </a>
                        </div>
                    </div>
                </div>
            `
        }
    };
    
    return templates[sequence] || templates.standard_sequence;
}

// Schedule follow-up emails (implement with your preferred job queue)
function scheduleFollowUpEmails(leadData, sequence) {
    // This would integrate with a job queue system like Bull, Agenda, or node-cron
    console.log(`Scheduling ${sequence} follow-up emails for ${leadData.email}`);
    
    // Example schedule:
    // Day 2: Success story email
    // Day 4: Educational content  
    // Day 7: Re-engagement if no response
    // etc.
}

// Estimate property value (implement with real estate API)
async function estimatePropertyValue(address) {
    if (!address) return null;
    
    // Integrate with Zillow API, RentSpider, or similar service
    // For now, return a placeholder
    return 500000; // Placeholder value
}

// Extract county from address
function extractCountyFromAddress(address) {
    if (!address) return 'Unknown';
    
    // Simple extraction - implement more sophisticated parsing
    const counties = ['Los Angeles', 'Orange', 'San Diego', 'Riverside', 'San Bernardino'];
    for (const county of counties) {
        if (address.toLowerCase().includes(county.toLowerCase())) {
            return county;
        }
    }
    return 'Unknown';
}

// Main lead capture endpoint
app.post('/api/lead-capture', async (req, res) => {
    try {
        const leadData = req.body;
        
        // Calculate lead score
        const score = calculateLeadScore(leadData);
        const priority = determinePriority(score);
        
        // Send to CRM
        await sendToCRM(leadData, score, priority);
        
        // Trigger email sequence
        if (leadData.email) {
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
    const notificationEmail = {
        from: '"Lead Alert System" <alerts@myforeclosuresolution.com>',
        to: 'help@myforeclosuresolution.com', // Your notification email
        subject: `🚨 HIGH PRIORITY LEAD - Score: ${score}`,
        html: `
            <h2>🚨 High Priority Lead Alert</h2>
            <p><strong>Score:</strong> ${score}</p>
            <p><strong>Name:</strong> ${leadData.name}</p>
            <p><strong>Email:</strong> ${leadData.email}</p>
            <p><strong>Phone:</strong> ${leadData.phone}</p>
            <p><strong>Situation:</strong> ${leadData.situation}</p>
            <p><strong>Property:</strong> ${leadData.property_address}</p>
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