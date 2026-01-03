/**
 * DIALOGFLOW CX WEBHOOK HANDLER
 * Processes voice assistant requests and integrates with other systems
 */

const { SessionsClient } = require('@google-cloud/dialogflow-cx');
const { VertexAI } = require('@google-cloud/vertexai');

// Initialize clients
const dialogflowClient = new SessionsClient();
const vertexAI = new VertexAI({
    project: 'foreclosure-ai-assistant',
    location: 'us-central1',
});

const geminiModel = vertexAI.preview.getGenerativeModel({
    model: 'gemini-1.5-pro',
});

/**
 * Main webhook handler for Dialogflow CX
 */
exports.dialogflowWebhook = async (req, res) => {
    const tag = req.body.fulfillmentInfo.tag;
    const parameters = req.body.sessionInfo.parameters;
    const languageCode = req.body.languageCode || 'en';

    console.log(`Webhook called with tag: ${tag}`);
    console.log(`Parameters:`, parameters);

    let response;

    try {
        switch (tag) {
            case 'urgent.assessment':
                response = await handleUrgentAssessment(parameters);
                break;

            case 'calculate.options':
                response = await calculateForeclosureOptions(parameters);
                break;

            case 'schedule.callback':
                response = await scheduleCallback(parameters);
                break;

            case 'provide.information':
                response = await provideInformation(parameters, languageCode);
                break;

            case 'transfer.human':
                response = await initiateTransfer(parameters);
                break;

            default:
                response = await handleGeneralQuery(parameters);
        }

        res.json(response);
    } catch (error) {
        console.error('Webhook error:', error);
        res.json({
            fulfillmentResponse: {
                messages: [{
                    text: {
                        text: ['I apologize, but I encountered an error. Let me transfer you to a specialist who can help.']
                    }
                }]
            },
            sessionInfo: {
                parameters: {
                    transfer_required: true
                }
            }
        });
    }
};

/**
 * Handle urgent foreclosure situations
 */
async function handleUrgentAssessment(parameters) {
    const { days_until_sale, county, amount_owed } = parameters;

    // Use Gemini to assess situation
    const prompt = `
    Assess this urgent foreclosure situation and provide immediate guidance:
    - Days until sale: ${days_until_sale}
    - County: ${county}
    - Amount owed: ${amount_owed}

    Provide:
    1. Urgency level (1-10)
    2. Can it be stopped? (yes/no/maybe)
    3. Immediate action required
    4. Success probability percentage

    Format as conversational response for phone call.
    `;

    const result = await geminiModel.generateContent({
        contents: [{ role: 'user', parts: [{ text: prompt }] }],
    });

    const analysis = await result.response.text();

    // Create urgent alert
    if (days_until_sale <= 7) {
        await createUrgentAlert({
            phone: parameters.phone_number,
            daysUntilSale: days_until_sale,
            county,
        });
    }

    return {
        fulfillmentResponse: {
            messages: [
                {
                    text: {
                        text: [analysis]
                    }
                },
                {
                    text: {
                        text: ['Would you like me to have a specialist call you back immediately?']
                    }
                }
            ]
        },
        sessionInfo: {
            parameters: {
                urgency_assessed: true,
                transfer_recommended: days_until_sale <= 7
            }
        }
    };
}

/**
 * Calculate and explain foreclosure options
 */
async function calculateForeclosureOptions(parameters) {
    const {
        property_value,
        mortgage_balance,
        monthly_income,
        can_afford_payment
    } = parameters;

    const equity = property_value - mortgage_balance;
    const options = [];

    // Determine available options
    if (equity > 0) {
        options.push({
            option: 'Quick Sale',
            description: 'Sell the property and keep the equity',
            pros: 'Walk away with cash, avoid foreclosure on credit',
            timeline: '7-14 days',
        });
    }

    if (can_afford_payment === 'yes') {
        options.push({
            option: 'Loan Modification',
            description: 'Restructure your loan for lower payments',
            pros: 'Keep your home, reduce monthly payment',
            timeline: '30-60 days',
        });
    }

    if (monthly_income > mortgage_balance * 0.003) {
        options.push({
            option: 'Repayment Plan',
            description: 'Catch up on payments over time',
            pros: 'Keep your home, manageable payment plan',
            timeline: '3-6 months',
        });
    }

    // Always available
    options.push({
        option: 'Short Sale',
        description: 'Sell for less than owed with bank approval',
        pros: 'Avoid foreclosure, less credit damage',
        timeline: '60-90 days',
    });

    // Format response
    const optionsText = options.map((opt, i) =>
        `Option ${i + 1}: ${opt.option}. ${opt.description} This typically takes ${opt.timeline}.`
    ).join(' ');

    return {
        fulfillmentResponse: {
            messages: [{
                text: {
                    text: [
                        `Based on your situation, you have ${options.length} potential options. ${optionsText} Which option sounds most interesting to you?`
                    ]
                }
            }]
        },
        sessionInfo: {
            parameters: {
                calculated_equity: equity,
                available_options: options.map(o => o.option),
                options_presented: true
            }
        }
    };
}

/**
 * Schedule callback appointment
 */
async function scheduleCallback(parameters) {
    const { preferred_time, phone_number, name } = parameters;

    // Create calendar appointment
    const appointment = {
        name,
        phone: phone_number,
        preferredTime: preferred_time,
        type: 'voice_assistant_callback',
        createdAt: new Date().toISOString(),
    };

    // Store in database
    await storeAppointment(appointment);

    // Send confirmation SMS
    await sendSMS(phone_number,
        `Appointment confirmed for ${preferred_time}. ` +
        `We'll call you at ${phone_number}. ` +
        `Reply CANCEL to cancel.`
    );

    return {
        fulfillmentResponse: {
            messages: [{
                text: {
                    text: [
                        `Perfect! I've scheduled a callback for ${preferred_time}. ` +
                        `A foreclosure specialist will call you at ${phone_number}. ` +
                        `You'll also receive a text confirmation. ` +
                        `Is there anything specific you'd like the specialist to know before they call?`
                    ]
                }
            }]
        },
        sessionInfo: {
            parameters: {
                callback_scheduled: true,
                appointment_id: appointment.id
            }
        }
    };
}

/**
 * Provide information based on query
 */
async function provideInformation(parameters, languageCode) {
    const { information_type, specific_question } = parameters;

    // Use Gemini for dynamic responses
    const prompt = `
    Answer this foreclosure-related question for California:
    Type: ${information_type}
    Question: ${specific_question}

    Provide a clear, concise answer suitable for phone conversation.
    Include specific California laws if relevant.
    ${languageCode === 'es' ? 'Answer in Spanish.' : ''}
    Keep response under 100 words.
    `;

    const result = await geminiModel.generateContent({
        contents: [{ role: 'user', parts: [{ text: prompt }] }],
    });

    const answer = await result.response.text();

    return {
        fulfillmentResponse: {
            messages: [{
                text: {
                    text: [answer, 'Does that answer your question?']
                }
            }]
        }
    };
}

/**
 * Transfer to human agent
 */
async function initiateTransfer(parameters) {
    const { reason, urgency_level } = parameters;

    // Log transfer request
    console.log(`Transfer requested: ${reason}, Urgency: ${urgency_level}`);

    // Determine best agent
    const agent = urgency_level > 7 ? 'senior_specialist' : 'general_support';

    return {
        fulfillmentResponse: {
            messages: [{
                text: {
                    text: [
                        'I understand you need to speak with a specialist. ' +
                        'Let me connect you right away. Please hold for just a moment.'
                    ]
                }
            }]
        },
        sessionInfo: {
            parameters: {
                transfer_to_agent: true,
                agent_type: agent,
                transfer_reason: reason
            }
        }
    };
}

/**
 * Handle general queries with Gemini
 */
async function handleGeneralQuery(parameters) {
    const query = parameters.query || parameters.text || '';

    const prompt = `
    You are a helpful voice assistant for My Foreclosure Solution.
    Answer this question about foreclosure help in California:
    "${query}"

    Keep response conversational and under 50 words.
    If you don't know, offer to connect them with a specialist.
    `;

    const result = await geminiModel.generateContent({
        contents: [{ role: 'user', parts: [{ text: prompt }] }],
    });

    const response = await result.response.text();

    return {
        fulfillmentResponse: {
            messages: [{
                text: { text: [response] }
            }]
        }
    };
}

/**
 * Helper functions
 */
async function createUrgentAlert(data) {
    // Send to CRM, Slack, SMS, etc.
    console.log('URGENT ALERT:', data);
}

async function storeAppointment(appointment) {
    // Store in database
    console.log('Storing appointment:', appointment);
}

async function sendSMS(phone, message) {
    // Twilio integration
    console.log(`SMS to ${phone}: ${message}`);
}

/**
 * Express app for local testing
 */
if (require.main === module) {
    const express = require('express');
    const app = express();
    app.use(express.json());

    app.post('/webhook', exports.dialogflowWebhook);

    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`Dialogflow webhook running on port ${PORT}`);
    });
}