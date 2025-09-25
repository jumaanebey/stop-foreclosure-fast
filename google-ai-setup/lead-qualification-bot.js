/**
 * LEAD QUALIFICATION BOT WITH GEMINI API
 * Automatically scores and qualifies foreclosure leads
 */

const { VertexAI } = require('@google-cloud/vertexai');
const { GoogleSpreadsheet } = require('google-spreadsheet');
const nodemailer = require('nodemailer');

// Initialize Vertex AI with Gemini
const vertexAI = new VertexAI({
    project: 'foreclosure-ai-assistant',
    location: 'us-central1',
});

const model = 'gemini-1.5-pro';
const generativeModel = vertexAI.preview.getGenerativeModel({
    model: model,
    generationConfig: {
        maxOutputTokens: 2048,
        temperature: 0.3,
        topP: 0.8,
    },
});

/**
 * Main Lead Qualification Function
 */
async function qualifyLead(leadData) {
    const {
        name,
        email,
        phone,
        propertyAddress,
        foreclosureStage,
        timelineUrgency,
        monthsBehind,
        propertyValue,
        mortgageBalance,
        additionalNotes
    } = leadData;

    // Create comprehensive prompt for Gemini
    const prompt = `
    Analyze this foreclosure lead and provide:
    1. Urgency Score (1-10)
    2. Qualification Score (1-10)
    3. Recommended Action
    4. Best Contact Method
    5. Personalized Message
    6. Risk Assessment

    Lead Information:
    - Name: ${name}
    - Property: ${propertyAddress}
    - Foreclosure Stage: ${foreclosureStage}
    - Timeline: ${timelineUrgency}
    - Months Behind: ${monthsBehind}
    - Property Value: $${propertyValue}
    - Mortgage Balance: $${mortgageBalance}
    - Notes: ${additionalNotes}

    Consider:
    - Equity position (value vs balance)
    - Time sensitivity
    - California foreclosure timeline
    - Likelihood of successful intervention

    Format response as JSON with keys: urgencyScore, qualificationScore,
    recommendedAction, contactMethod, personalizedMessage, riskAssessment,
    estimatedEquity, interventionStrategy
    `;

    try {
        // Get Gemini's analysis
        const result = await generativeModel.generateContent({
            contents: [{ role: 'user', parts: [{ text: prompt }] }],
        });

        const response = await result.response;
        const analysisText = response.text();

        // Parse JSON response
        const analysis = JSON.parse(
            analysisText.replace(/```json\n?|\n?```/g, '')
        );

        // Add timestamp and lead ID
        analysis.leadId = generateLeadId();
        analysis.analyzedAt = new Date().toISOString();
        analysis.leadData = leadData;

        return analysis;
    } catch (error) {
        console.error('Gemini API Error:', error);
        throw error;
    }
}

/**
 * Automated Response System
 */
async function generateAutoResponse(analysis) {
    const { urgencyScore, personalizedMessage, contactMethod, leadData } = analysis;

    // High urgency (8-10): Immediate action
    if (urgencyScore >= 8) {
        await sendUrgentAlert(analysis);
        await scheduleImmediateCallback(analysis);
        await sendSMS(leadData.phone,
            "URGENT: We received your foreclosure help request. " +
            "A specialist will call you within 30 minutes. " +
            "Reply STOP to opt out."
        );
    }
    // Medium urgency (5-7): Same day response
    else if (urgencyScore >= 5) {
        await sendEmail(leadData.email, personalizedMessage);
        await scheduleCallback(analysis, 'today');
    }
    // Low urgency (1-4): Next day response
    else {
        await sendEmail(leadData.email, personalizedMessage);
        await scheduleCallback(analysis, 'tomorrow');
    }

    // Store in database
    await storeLead(analysis);

    // Update Google Sheets
    await updateSpreadsheet(analysis);
}

/**
 * Google Sheets Integration
 */
async function updateSpreadsheet(analysis) {
    const doc = new GoogleSpreadsheet('YOUR_SHEET_ID');
    await doc.useServiceAccountAuth({
        client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
        private_key: process.env.GOOGLE_PRIVATE_KEY,
    });

    await doc.loadInfo();
    const sheet = doc.sheetsByIndex[0];

    await sheet.addRow({
        'Lead ID': analysis.leadId,
        'Name': analysis.leadData.name,
        'Email': analysis.leadData.email,
        'Phone': analysis.leadData.phone,
        'Urgency Score': analysis.urgencyScore,
        'Qualification Score': analysis.qualificationScore,
        'Recommended Action': analysis.recommendedAction,
        'Equity': analysis.estimatedEquity,
        'Status': 'New',
        'Assigned To': getAssignedAgent(analysis),
        'Created': new Date().toISOString(),
    });
}

/**
 * Smart Lead Routing
 */
function getAssignedAgent(analysis) {
    const { urgencyScore, qualificationScore, leadData } = analysis;

    // Route based on score and location
    if (urgencyScore >= 8 && qualificationScore >= 8) {
        return 'Senior Specialist - Immediate';
    } else if (urgencyScore >= 5) {
        return 'Foreclosure Team - Priority';
    } else {
        return 'General Team - Standard';
    }
}

/**
 * Send Urgent Alert to Team
 */
async function sendUrgentAlert(analysis) {
    const { leadData, urgencyScore, estimatedEquity } = analysis;

    const alertMessage = `
    🚨 URGENT FORECLOSURE LEAD 🚨

    Score: ${urgencyScore}/10
    Name: ${leadData.name}
    Phone: ${leadData.phone}
    Equity: $${estimatedEquity}
    Stage: ${leadData.foreclosureStage}

    ACTION REQUIRED: Call immediately!
    `;

    // Send to Slack
    await sendToSlack('#urgent-leads', alertMessage);

    // Send SMS to on-duty specialist
    await sendSMS(process.env.SPECIALIST_PHONE, alertMessage);
}

/**
 * Helper Functions
 */
function generateLeadId() {
    return `FCL-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

async function sendEmail(to, message) {
    const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
            user: process.env.EMAIL_USER,
            pass: process.env.EMAIL_PASSWORD,
        },
    });

    await transporter.sendMail({
        from: 'help@myforeclosuresolution.com',
        to: to,
        subject: 'Your Foreclosure Help Request - We Can Help',
        html: message,
    });
}

async function sendSMS(phone, message) {
    // Using Twilio
    const twilio = require('twilio')(
        process.env.TWILIO_ACCOUNT_SID,
        process.env.TWILIO_AUTH_TOKEN
    );

    await twilio.messages.create({
        body: message,
        from: process.env.TWILIO_PHONE,
        to: phone,
    });
}

async function sendToSlack(channel, message) {
    // Implement Slack webhook
    const webhook = process.env.SLACK_WEBHOOK_URL;
    await fetch(webhook, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: message, channel: channel }),
    });
}

async function scheduleCallback(analysis, when) {
    // Integrate with calendar API
    console.log(`Scheduling callback for ${when}`);
}

async function scheduleImmediateCallback(analysis) {
    // Trigger immediate call system
    console.log('Triggering immediate callback');
}

async function storeLead(analysis) {
    // Store in Firestore or your database
    console.log('Storing lead in database');
}

/**
 * Express Webhook Endpoint
 */
const express = require('express');
const app = express();
app.use(express.json());

app.post('/api/qualify-lead', async (req, res) => {
    try {
        const leadData = req.body;

        // Qualify lead with Gemini
        const analysis = await qualifyLead(leadData);

        // Generate automated response
        await generateAutoResponse(analysis);

        // Return analysis to frontend
        res.json({
            success: true,
            leadId: analysis.leadId,
            urgencyScore: analysis.urgencyScore,
            message: 'Lead processed successfully',
            nextSteps: analysis.recommendedAction,
        });
    } catch (error) {
        console.error('Lead qualification error:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to process lead',
        });
    }
});

// Cloud Function Export
exports.qualifyForeclosureLead = async (req, res) => {
    await app(req, res);
};

// Local testing
if (require.main === module) {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`Lead Qualification Bot running on port ${PORT}`);
    });
}

module.exports = { qualifyLead, generateAutoResponse };