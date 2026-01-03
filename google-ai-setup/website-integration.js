/**
 * WEBSITE INTEGRATION FOR AI WORKFLOWS
 * Add this to your foreclosure website to use AI features
 */

// Configuration
const AI_CONFIG = {
    // Local testing endpoints
    LOCAL_BASE_URL: 'http://localhost:8080/api',

    // Cloud Function endpoints (update after deployment)
    CLOUD_BASE_URL: 'https://us-central1-impactful-veld-469306-c7.cloudfunctions.net',

    // Use local for testing, cloud for production
    USE_CLOUD: false
};

/**
 * Lead Qualification Integration
 */
class LeadQualificationIntegration {
    constructor() {
        this.baseUrl = AI_CONFIG.USE_CLOUD ? AI_CONFIG.CLOUD_BASE_URL : AI_CONFIG.LOCAL_BASE_URL;
    }

    /**
     * Qualify lead when form is submitted
     */
    async qualifyLead(formData) {
        const leadData = {
            name: formData.get('name'),
            email: formData.get('email'),
            phone: formData.get('phone'),
            propertyAddress: formData.get('address'),
            foreclosureStage: formData.get('stage') || 'unknown',
            timelineUrgency: formData.get('timeline'),
            monthsBehind: parseInt(formData.get('months_behind')) || 0,
            propertyValue: parseFloat(formData.get('property_value')) || 0,
            mortgageBalance: parseFloat(formData.get('mortgage_balance')) || 0,
            additionalNotes: formData.get('notes') || ''
        };

        try {
            const response = await fetch(`${this.baseUrl}/qualify-lead`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(leadData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            // Handle the AI response
            this.handleLeadQualification(result, leadData);

            return result;
        } catch (error) {
            console.error('Lead qualification failed:', error);
            // Fallback to manual processing
            this.fallbackProcessing(leadData);
            return null;
        }
    }

    /**
     * Handle AI qualification results
     */
    handleLeadQualification(aiResult, originalData) {
        const { urgencyScore, leadId, nextSteps } = aiResult;

        // Show appropriate thank you message based on urgency
        if (urgencyScore >= 8) {
            this.showUrgentMessage(leadId);
        } else if (urgencyScore >= 5) {
            this.showPriorityMessage(leadId);
        } else {
            this.showStandardMessage(leadId);
        }

        // Track analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', 'lead_qualified', {
                'event_category': 'ai_processing',
                'urgency_score': urgencyScore,
                'lead_id': leadId
            });
        }
    }

    showUrgentMessage(leadId) {
        const messageHtml = `
            <div class="ai-response urgent">
                <div class="success-icon">🚨</div>
                <h3>URGENT: We'll Contact You Immediately</h3>
                <p>Based on your situation, time is critical. A foreclosure specialist will call you within 30 minutes.</p>
                <div class="next-steps">
                    <p><strong>What happens next:</strong></p>
                    <ul>
                        <li>Specialist calls you in 30 minutes</li>
                        <li>Review your options immediately</li>
                        <li>Get same-day action plan</li>
                    </ul>
                </div>
                <p class="reference">Reference ID: ${leadId}</p>
                <div class="contact-backup">
                    <p>Need immediate help? Call: <a href="tel:+1-949-565-5285">(949) 565-5285</a></p>
                </div>
            </div>
        `;
        this.displayMessage(messageHtml);
    }

    showPriorityMessage(leadId) {
        const messageHtml = `
            <div class="ai-response priority">
                <div class="success-icon">⚡</div>
                <h3>Priority Response - We'll Call Today</h3>
                <p>Your situation requires prompt attention. We'll contact you within 4 hours.</p>
                <div class="next-steps">
                    <p><strong>What we'll discuss:</strong></p>
                    <ul>
                        <li>Review your specific timeline</li>
                        <li>Explain your available options</li>
                        <li>Create an action plan</li>
                    </ul>
                </div>
                <p class="reference">Reference ID: ${leadId}</p>
            </div>
        `;
        this.displayMessage(messageHtml);
    }

    showStandardMessage(leadId) {
        const messageHtml = `
            <div class="ai-response standard">
                <div class="success-icon">✅</div>
                <h3>Thank You - We'll Be In Touch Soon</h3>
                <p>We've received your information and will contact you within 24 hours.</p>
                <div class="next-steps">
                    <p><strong>What to expect:</strong></p>
                    <ul>
                        <li>Detailed review of your situation</li>
                        <li>Explanation of all available options</li>
                        <li>No-obligation consultation</li>
                    </ul>
                </div>
                <p class="reference">Reference ID: ${leadId}</p>
                <div class="resources">
                    <p><strong>In the meantime:</strong></p>
                    <a href="/california-foreclosure-timeline.pdf" class="resource-link">Download CA Foreclosure Timeline</a>
                </div>
            </div>
        `;
        this.displayMessage(messageHtml);
    }

    displayMessage(html) {
        // Replace form with success message
        const form = document.querySelector('form.lead-form');
        if (form) {
            form.innerHTML = html;
            form.scrollIntoView({ behavior: 'smooth' });
        }
    }

    fallbackProcessing(leadData) {
        // Show generic success message if AI fails
        const messageHtml = `
            <div class="ai-response fallback">
                <div class="success-icon">📞</div>
                <h3>Thank You - We'll Contact You Soon</h3>
                <p>We've received your information and will contact you shortly.</p>
                <p>For immediate assistance: <a href="tel:+1-949-565-5285">(949) 565-5285</a></p>
            </div>
        `;
        this.displayMessage(messageHtml);
    }
}

/**
 * Document Upload Integration
 */
class DocumentUploadIntegration {
    constructor() {
        this.baseUrl = AI_CONFIG.USE_CLOUD ? AI_CONFIG.CLOUD_BASE_URL : AI_CONFIG.LOCAL_BASE_URL;
    }

    async processDocument(file, documentType = 'auto-detect') {
        const formData = new FormData();
        formData.append('document', file);
        formData.append('documentType', documentType);

        try {
            const response = await fetch(`${this.baseUrl}/process-document`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            this.displayDocumentResults(result);
            return result;
        } catch (error) {
            console.error('Document processing failed:', error);
            this.showDocumentError();
        }
    }

    displayDocumentResults(result) {
        const { urgencyScore, actionItems, extractedData } = result;

        let urgencyClass = 'low';
        if (urgencyScore >= 8) urgencyClass = 'critical';
        else if (urgencyScore >= 6) urgencyClass = 'high';

        const html = `
            <div class="document-results ${urgencyClass}">
                <h4>Document Analysis Complete</h4>
                <div class="urgency-indicator">
                    Urgency Level: <span class="score">${urgencyScore}/10</span>
                </div>

                ${actionItems.length > 0 ? `
                    <div class="action-items">
                        <h5>Recommended Actions:</h5>
                        <ul>
                            ${actionItems.map(item =>
                                `<li class="priority-${item.priority.toLowerCase()}">
                                    <strong>${item.action}</strong>
                                    ${item.deadline ? ` - ${item.deadline}` : ''}
                                </li>`
                            ).join('')}
                        </ul>
                    </div>
                ` : ''}

                <div class="next-step">
                    <button onclick="scheduleConsultation()" class="cta-button">
                        Schedule Free Consultation
                    </button>
                </div>
            </div>
        `;

        document.getElementById('document-results').innerHTML = html;
    }
}

/**
 * Initialize AI Integration
 */
function initializeAIIntegration() {
    const leadQualifier = new LeadQualificationIntegration();
    const documentProcessor = new DocumentUploadIntegration();

    // Hook into main form submission
    const mainForm = document.querySelector('.lead-form, .contact-form, #prequal-form');
    if (mainForm) {
        mainForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Show loading state
            const submitBtn = mainForm.querySelector('[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Processing with AI...';
            submitBtn.disabled = true;

            try {
                const formData = new FormData(mainForm);
                await leadQualifier.qualifyLead(formData);
            } catch (error) {
                console.error('Form processing error:', error);
                // Restore button and show error
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // Hook into document upload
    const documentInput = document.querySelector('input[type="file"]');
    if (documentInput) {
        documentInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (file && file.type === 'application/pdf') {
                await documentProcessor.processDocument(file);
            }
        });
    }

    console.log('🤖 AI Integration initialized');
}

/**
 * Schedule Consultation (called from AI results)
 */
function scheduleConsultation() {
    // Scroll to calendar or show modal
    const calendarElement = document.getElementById('calendar-widget');
    if (calendarElement) {
        calendarElement.scrollIntoView({ behavior: 'smooth' });
    } else {
        // Fallback to phone call
        window.location.href = 'tel:+1-949-565-5285';
    }
}

// Auto-initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAIIntegration);
} else {
    initializeAIIntegration();
}

// Export for manual initialization if needed
window.ForecastureAI = {
    LeadQualificationIntegration,
    DocumentUploadIntegration,
    initializeAIIntegration
};