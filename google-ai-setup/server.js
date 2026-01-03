/**
 * Express Server for Foreclosure AI Workflows
 * Deploys to Cloud Run for easier deployment
 */

const express = require('express');
const cors = require('cors');
const twilio = require('twilio');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 8080;

// Initialize Twilio client
const twilioAccountSid = process.env.TWILIO_ACCOUNT_SID;
const twilioAuthToken = process.env.TWILIO_AUTH_TOKEN;
const twilioPhoneNumber = process.env.TWILIO_PHONE;

const twilioClient = twilio(twilioAccountSid, twilioAuthToken);

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Health check
app.get('/', (req, res) => {
    res.json({
        service: 'Foreclosure AI Workflows',
        status: 'running',
        version: '1.0.0',
        timestamp: new Date().toISOString()
    });
});

// Lead Qualification Endpoint
app.post('/api/qualify-lead', (req, res) => {
    try {
        const leadData = req.body;
        console.log('Processing lead:', leadData);

        // Calculate urgency score
        let urgencyScore = 5;

        // Timeline urgency
        if (leadData.timelineUrgency) {
            const timelineStr = leadData.timelineUrgency.toLowerCase();
            if (timelineStr.includes('day')) {
                const days = parseInt(timelineStr) || 30;
                if (days <= 7) urgencyScore = 10;
                else if (days <= 14) urgencyScore = 9;
                else if (days <= 30) urgencyScore = 8;
                else if (days <= 60) urgencyScore = 6;
            }
        }

        // Stage urgency
        if (leadData.foreclosureStage) {
            const stage = leadData.foreclosureStage.toLowerCase();
            if (stage.includes('sale') || stage.includes('auction')) urgencyScore = 10;
            else if (stage.includes('default')) urgencyScore = Math.max(urgencyScore, 7);
        }

        // Months behind
        if (leadData.monthsBehind >= 6) urgencyScore += 1;
        if (leadData.monthsBehind >= 12) urgencyScore += 1;

        // Calculate qualification score
        let qualificationScore = 5;

        // Equity calculation
        const propertyValue = parseFloat(leadData.propertyValue) || 0;
        const mortgageBalance = parseFloat(leadData.mortgageBalance) || 0;
        const equity = propertyValue - mortgageBalance;

        if (equity > 50000) qualificationScore = 9;
        else if (equity > 20000) qualificationScore = 8;
        else if (equity > 0) qualificationScore = 7;
        else if (equity > -50000) qualificationScore = 6;

        // Generate lead ID
        const leadId = `FCL-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        // Create response
        const response = {
            success: true,
            leadId,
            urgencyScore: Math.min(Math.max(urgencyScore, 1), 10),
            qualificationScore: Math.min(Math.max(qualificationScore, 1), 10),
            estimatedEquity: equity,
            message: 'Lead qualified successfully',
            nextSteps: urgencyScore >= 8 ?
                'URGENT: Immediate callback scheduled' :
                'Standard response within 24 hours',
            recommendedAction: urgencyScore >= 8 ?
                'Contact within 2 hours - high priority case' :
                urgencyScore >= 6 ?
                'Contact today - moderate urgency' :
                'Contact within 24-48 hours',
            routing: {
                department: urgencyScore >= 8 ? 'urgent' : 'general',
                priority: urgencyScore >= 8 ? 'high' : 'normal'
            }
        };

        // Log for analytics
        console.log(`Lead qualified: ${leadId}, Urgency: ${response.urgencyScore}, Equity: $${equity}`);

        res.json(response);
    } catch (error) {
        console.error('Lead qualification error:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to process lead',
            message: 'Please try again or call (949) 565-5285 directly'
        });
    }
});

// SMS Sending Endpoint
app.post('/api/send-sms', async (req, res) => {
    try {
        const { phone, message, leadName, timeline } = req.body;

        console.log('Sending SMS to:', phone);

        // Send SMS via Twilio
        const smsResult = await twilioClient.messages.create({
            body: message,
            from: twilioPhoneNumber,
            to: phone
        });

        console.log('SMS sent successfully:', smsResult.sid);

        // Schedule follow-up messages
        if (timeline === '7days') {
            // Schedule urgent follow-up in 5 minutes
            setTimeout(async () => {
                const followUpMessage = `${leadName}, your foreclosure is CRITICAL. I'm standing by to help right now. Call immediately: (949) 565-5285 or reply HELP`;

                try {
                    await twilioClient.messages.create({
                        body: followUpMessage,
                        from: twilioPhoneNumber,
                        to: phone
                    });
                    console.log('5-minute follow-up sent to:', phone);
                } catch (error) {
                    console.error('Follow-up SMS error:', error);
                }
            }, 5 * 60 * 1000);
        }

        res.json({
            success: true,
            messageSid: smsResult.sid,
            status: 'sent'
        });

    } catch (error) {
        console.error('SMS sending error:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to send SMS',
            message: error.message
        });
    }
});

// Document Processing Endpoint (Mock for now)
app.post('/api/process-document', (req, res) => {
    try {
        const documentType = req.body.documentType || 'unknown';

        // Mock analysis based on document type
        let urgencyScore = 5;
        let actionItems = [];

        if (documentType.includes('sale') || documentType.includes('auction')) {
            urgencyScore = 10;
            actionItems = [
                { priority: 'CRITICAL', action: 'File postponement request', deadline: 'Immediately' },
                { priority: 'CRITICAL', action: 'Contact homeowner urgently', deadline: 'Within 1 hour' }
            ];
        } else if (documentType.includes('default')) {
            urgencyScore = 8;
            actionItems = [
                { priority: 'HIGH', action: 'Contact homeowner', deadline: 'Within 24 hours' },
                { priority: 'HIGH', action: 'Calculate reinstatement amount', deadline: 'Today' }
            ];
        }

        const documentId = `DOC-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        res.json({
            success: true,
            documentId,
            urgencyScore,
            extractedData: {
                documentType,
                processedAt: new Date().toISOString()
            },
            actionItems,
            message: 'Document processed successfully'
        });
    } catch (error) {
        console.error('Document processing error:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to process document'
        });
    }
});

// Email Processing Endpoint (Mock)
app.post('/api/process-email', (req, res) => {
    const { senderName, message, urgencyLevel } = req.body;

    const messageId = `EMAIL-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    res.json({
        success: true,
        messageId,
        subject: `Re: Your foreclosure assistance inquiry`,
        preview: `Hi ${senderName}, thank you for reaching out. We understand this is a stressful situation...`,
        response: 'Personalized email response generated and queued for sending'
    });
});

// Test endpoint
app.get('/api/test', (req, res) => {
    res.json({
        message: 'All systems operational',
        timestamp: new Date().toISOString(),
        endpoints: [
            'POST /api/qualify-lead',
            'POST /api/process-document',
            'POST /api/process-email'
        ]
    });
});

app.listen(PORT, () => {
    console.log(`🚀 Foreclosure AI server running on port ${PORT}`);
    console.log(`🌟 Health check: http://localhost:${PORT}`);
    console.log(`🤖 API endpoints: http://localhost:${PORT}/api/test`);
});

module.exports = app;