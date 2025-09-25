/**
 * SMART EMAIL RESPONSE SYSTEM WITH GEMINI
 * Automated, personalized email responses for foreclosure inquiries
 */

const { VertexAI } = require('@google-cloud/vertexai');
const nodemailer = require('nodemailer');
const { google } = require('googleapis');
const { JWT } = require('google-auth-library');

// Initialize Gemini
const vertexAI = new VertexAI({
    project: 'foreclosure-ai-assistant',
    location: 'us-central1',
});

const geminiModel = vertexAI.preview.getGenerativeModel({
    model: 'gemini-1.5-pro',
    generationConfig: {
        temperature: 0.7, // More creative for emails
        maxOutputTokens: 1024,
    },
});

/**
 * Email Templates Library
 */
const EMAIL_TEMPLATES = {
    URGENT_RESPONSE: 'urgent_foreclosure_help',
    INITIAL_INQUIRY: 'general_inquiry',
    DOCUMENT_REQUEST: 'need_documents',
    APPOINTMENT_CONFIRM: 'appointment_scheduled',
    FOLLOW_UP: 'follow_up_check',
    SPANISH: 'spanish_response',
};

/**
 * Smart Email Response Generator
 */
class SmartEmailResponder {
    constructor() {
        this.gmailAuth = this.setupGmailAuth();
        this.emailTransporter = this.setupEmailTransporter();
    }

    /**
     * Generate personalized email response
     */
    async generateResponse(inquiry) {
        const {
            senderEmail,
            senderName,
            subject,
            message,
            language = 'en',
            urgencyLevel,
            previousInteractions = 0,
        } = inquiry;

        // Analyze email intent with Gemini
        const intent = await this.analyzeEmailIntent(subject, message);

        // Generate personalized response
        const response = await this.createPersonalizedResponse({
            intent,
            senderName,
            message,
            language,
            urgencyLevel,
            previousInteractions,
        });

        // Add appropriate attachments/resources
        const resources = await this.selectResources(intent);

        // Schedule follow-up if needed
        if (intent.requiresFollowUp) {
            await this.scheduleFollowUp(senderEmail, intent.followUpDays);
        }

        return {
            to: senderEmail,
            subject: response.subject,
            body: response.body,
            attachments: resources,
            followUpScheduled: intent.requiresFollowUp,
        };
    }

    /**
     * Analyze email intent using Gemini
     */
    async analyzeEmailIntent(subject, message) {
        const prompt = `
        Analyze this foreclosure inquiry email and determine:

        Subject: ${subject}
        Message: ${message}

        Provide analysis in JSON format:
        1. primaryIntent: (options: urgent_help, information_request, document_submission,
                          appointment_request, follow_up, complaint, success_story)
        2. urgencyScore: (1-10)
        3. emotionalTone: (desperate, anxious, confused, hopeful, angry, grateful)
        4. keyTopics: [array of main topics]
        5. requiresFollowUp: boolean
        6. followUpDays: number
        7. suggestedResponseType: (immediate, same_day, next_day, scheduled)
        8. language: (en, es, other)
        9. hasDocuments: boolean
        10. questionsAsked: [array of specific questions]
        `;

        const result = await geminiModel.generateContent({
            contents: [{ role: 'user', parts: [{ text: prompt }] }],
        });

        const response = await result.response;
        return JSON.parse(response.text().replace(/```json\n?|\n?```/g, ''));
    }

    /**
     * Create personalized response with Gemini
     */
    async createPersonalizedResponse(params) {
        const {
            intent,
            senderName,
            message,
            language,
            urgencyLevel,
            previousInteractions,
        } = params;

        // Build context-aware prompt
        const prompt = `
        Create a personalized, empathetic email response for a homeowner facing foreclosure.

        Context:
        - Recipient Name: ${senderName}
        - Their Concern: ${message}
        - Urgency Level: ${urgencyLevel}/10
        - Emotional Tone: ${intent.emotionalTone}
        - Previous Interactions: ${previousInteractions}
        - Language: ${language === 'es' ? 'Spanish' : 'English'}

        Requirements:
        1. Be empathetic and understanding
        2. Provide specific, actionable next steps
        3. Include our phone number: (949) 328-4811
        4. Mention free consultation
        5. Address their specific questions: ${intent.questionsAsked.join(', ')}
        6. Keep professional but warm tone
        7. Include urgency-appropriate call to action
        8. Mention California-specific information if relevant

        Format response as JSON with:
        - subject: compelling subject line
        - greeting: personalized greeting
        - body: main email content (use HTML formatting)
        - signature: professional signature
        - ps: optional postscript for urgency

        ${language === 'es' ? 'Write entirely in Spanish.' : ''}
        `;

        const result = await geminiModel.generateContent({
            contents: [{ role: 'user', parts: [{ text: prompt }] }],
        });

        const response = await result.response;
        const emailContent = JSON.parse(
            response.text().replace(/```json\n?|\n?```/g, '')
        );

        // Combine all parts into final email
        return {
            subject: emailContent.subject,
            body: this.formatEmailHTML(emailContent),
        };
    }

    /**
     * Format email with professional HTML template
     */
    formatEmailHTML(content) {
        return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                }
                .header {
                    background: linear-gradient(135deg, #0d9488, #14b8a6);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }
                .content {
                    padding: 30px;
                    background: #f9fafb;
                    border: 1px solid #e5e7eb;
                }
                .cta-button {
                    display: inline-block;
                    background: #ea580c;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    margin: 20px 0;
                    font-weight: bold;
                }
                .footer {
                    background: #1f2937;
                    color: #9ca3af;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                }
                .urgency-banner {
                    background: #fee2e2;
                    border-left: 4px solid #ef4444;
                    padding: 10px;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>My Foreclosure Solution</h1>
                <p>California's Trusted Foreclosure Prevention Specialists</p>
            </div>

            <div class="content">
                ${content.greeting}

                ${content.body}

                <div style="text-align: center;">
                    <a href="tel:+1-949-328-4811" class="cta-button">
                        Call Now: (949) 328-4811
                    </a>
                </div>

                ${content.ps ? `<p><strong>P.S.</strong> ${content.ps}</p>` : ''}
            </div>

            <div class="footer">
                ${content.signature}
                <hr style="border: none; border-top: 1px solid #4b5563; margin: 20px 0;">
                <p>
                    California DRE License #02076038 | NMLS #2033637<br>
                    This email contains confidential information intended solely for the recipient.
                </p>
            </div>
        </body>
        </html>
        `;
    }

    /**
     * Select appropriate resources based on intent
     */
    async selectResources(intent) {
        const resources = [];

        // Map intents to resources
        const resourceMap = {
            urgent_help: ['california-foreclosure-timeline.pdf', 'emergency-options.pdf'],
            information_request: ['foreclosure-guide.pdf', 'faq.pdf'],
            document_submission: ['document-checklist.pdf'],
            appointment_request: ['preparation-guide.pdf'],
        };

        const selectedFiles = resourceMap[intent.primaryIntent] || [];

        // Add language-specific resources
        if (intent.language === 'es') {
            selectedFiles.push('guia-español.pdf');
        }

        return selectedFiles;
    }

    /**
     * Auto-categorize and route emails
     */
    async routeEmail(inquiry, intent) {
        const routing = {
            department: 'general',
            priority: 'normal',
            assignedTo: null,
        };

        // High urgency routing
        if (intent.urgencyScore >= 8) {
            routing.department = 'urgent';
            routing.priority = 'high';
            routing.assignedTo = 'senior-specialist';
        }
        // Document submission
        else if (intent.hasDocuments) {
            routing.department = 'processing';
            routing.priority = 'normal';
            routing.assignedTo = 'document-team';
        }
        // Spanish language support
        else if (intent.language === 'es') {
            routing.department = 'spanish-support';
            routing.assignedTo = 'bilingual-team';
        }

        return routing;
    }

    /**
     * Schedule automated follow-ups
     */
    async scheduleFollowUp(email, daysDelay) {
        const followUpDate = new Date();
        followUpDate.setDate(followUpDate.getDate() + daysDelay);

        // Store in database or scheduler
        const followUp = {
            email,
            scheduledFor: followUpDate,
            template: 'follow_up',
            status: 'pending',
        };

        console.log(`Follow-up scheduled for ${email} on ${followUpDate}`);
        return followUp;
    }

    /**
     * Setup Gmail API authentication
     */
    setupGmailAuth() {
        const auth = new JWT({
            email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
            key: process.env.GOOGLE_PRIVATE_KEY,
            scopes: ['https://www.googleapis.com/auth/gmail.send'],
        });
        return auth;
    }

    /**
     * Setup email transporter
     */
    setupEmailTransporter() {
        return nodemailer.createTransport({
            service: 'gmail',
            auth: {
                user: process.env.EMAIL_USER,
                pass: process.env.EMAIL_APP_PASSWORD,
            },
        });
    }

    /**
     * Send email with tracking
     */
    async sendEmail(emailData) {
        const { to, subject, body, attachments = [] } = emailData;

        const mailOptions = {
            from: '"My Foreclosure Solution" <help@myforeclosuresolution.com>',
            to,
            subject,
            html: body,
            attachments: attachments.map(file => ({
                filename: file,
                path: `./resources/${file}`,
            })),
        };

        try {
            const info = await this.emailTransporter.sendMail(mailOptions);

            // Track email metrics
            await this.trackEmailMetrics({
                messageId: info.messageId,
                to,
                subject,
                sentAt: new Date(),
                status: 'sent',
            });

            return { success: true, messageId: info.messageId };
        } catch (error) {
            console.error('Email send error:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Track email metrics for optimization
     */
    async trackEmailMetrics(metrics) {
        // Log to BigQuery or your analytics platform
        console.log('Email metrics:', metrics);
    }
}

/**
 * Express webhook for email processing
 */
const express = require('express');
const app = express();
app.use(express.json());

app.post('/api/process-email', async (req, res) => {
    try {
        const responder = new SmartEmailResponder();

        // Generate response
        const emailResponse = await responder.generateResponse(req.body);

        // Send email
        const result = await responder.sendEmail(emailResponse);

        res.json({
            success: true,
            messageId: result.messageId,
            response: 'Email processed and sent successfully',
        });
    } catch (error) {
        console.error('Email processing error:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to process email',
        });
    }
});

// Cloud Function export
exports.processForeclosureEmail = async (req, res) => {
    await app(req, res);
};

module.exports = SmartEmailResponder;