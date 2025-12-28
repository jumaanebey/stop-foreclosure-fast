/**
 * AI Integration for My Foreclosure Solution
 * Add this to your existing script.js or upload as separate file
 */

// YOUR LIVE AI API URL
const AI_API_URL = 'https://stop-foreclosure-fast.onrender.com';

// AI-Enhanced Lead Processing
class ForeclosureAI {
    constructor() {
        this.apiUrl = AI_API_URL;
        this.fallbackMode = false;
        this.initializeAI();
    }

    async initializeAI() {
        try {
            const response = await fetch(`${this.apiUrl}/api/ai/health`);
            if (response.ok) {
                console.log('🤖 AI System Online');
                this.enhanceWebsite();
            }
        } catch (error) {
            console.log('🔄 AI Unavailable - Using Standard Mode');
            this.fallbackMode = true;
        }
    }

    enhanceWebsite() {
        this.addRealTimeUrgencyDetection();
        this.enhanceFormSubmissions();
        this.addPropertyAnalysis();
        this.setupBehavioralTracking();
    }

    // Real-time urgency detection as user types
    addRealTimeUrgencyDetection() {
        const situationField = document.querySelector('[name="situation"]');
        if (!situationField) return;

        let urgencyTimeout;
        situationField.addEventListener('input', () => {
            clearTimeout(urgencyTimeout);
            urgencyTimeout = setTimeout(() => {
                this.analyzeUrgency(situationField.value);
            }, 2000); // Analyze after 2 seconds of no typing
        });
    }

    async analyzeUrgency(situationText) {
        if (this.fallbackMode || !situationText || situationText.length < 20) return;

        try {
            const response = await fetch(`${this.apiUrl}/api/ai/analyze-urgency`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    situation: situationText,
                    timestamp: new Date().toISOString()
                })
            });

            const result = await response.json();
            
            if (result.success && result.escalate) {
                this.showEmergencyAssistance(result);
            }
        } catch (error) {
            console.log('Urgency analysis unavailable');
        }
    }

    showEmergencyAssistance(urgencyResult) {
        // Remove existing emergency popup
        const existing = document.querySelector('.emergency-assistance');
        if (existing) existing.remove();

        const popup = document.createElement('div');
        popup.className = 'emergency-assistance';
        popup.innerHTML = `
            <div class="emergency-content">
                <div class="emergency-header">
                    <span class="emergency-icon">🚨</span>
                    <h3>Emergency Foreclosure Situation Detected</h3>
                </div>
                
                <div class="emergency-details">
                    <p><strong>Urgency Level:</strong> ${urgencyResult.urgency_level.toUpperCase()}</p>
                    <p><strong>Action Required:</strong> ${urgencyResult.action_required}</p>
                    
                    ${urgencyResult.keywords_detected.length > 0 ? `
                    <div class="keywords-detected">
                        <small><strong>Keywords found:</strong> ${urgencyResult.keywords_detected.join(', ')}</small>
                    </div>
                    ` : ''}
                </div>
                
                <div class="emergency-actions">
                    <button class="emergency-call-btn" onclick="window.open('tel:9495655285')">
                        📞 Call Emergency Line Now
                    </button>
                    <button class="priority-form-btn" onclick="foreclosureAI.showPriorityForm()">
                        ⚡ Priority Consultation
                    </button>
                </div>
                
                <button class="close-emergency" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        document.body.appendChild(popup);

        // Track emergency detection
        if (typeof gtag !== 'undefined') {
            gtag('event', 'emergency_detected', {
                'event_category': 'AI Analysis',
                'urgency_level': urgencyResult.urgency_level,
                'keywords': urgencyResult.keywords_detected.join(', ')
            });
        }

        // Auto-remove after 45 seconds
        setTimeout(() => {
            if (popup.parentElement) popup.remove();
        }, 45000);
    }

    // Enhanced form submission with AI scoring
    enhanceFormSubmissions() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAIEnhancedSubmission(form);
            });
        });
    }

    async handleAIEnhancedSubmission(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Add tracking data
        data.session_data = this.getSessionData();
        data.form_type = 'contact';
        data.device_type = this.getDeviceType();
        data.lead_source = this.getTrafficSource();
        data.timestamp = new Date().toISOString();

        // Show loading state
        this.showFormLoading(form);

        try {
            // Get AI enhancement
            const aiResult = await this.scoreLeadWithAI(data);
            
            // Submit with AI data
            await this.submitEnhancedLead(data, aiResult);
            
            // Show appropriate response based on AI score
            this.showAIEnhancedResponse(aiResult);
            
        } catch (error) {
            console.log('AI enhancement failed, using standard submission');
            this.submitStandardForm(data);
        }
    }

    async scoreLeadWithAI(leadData) {
        if (this.fallbackMode) return null;

        try {
            const response = await fetch(`${this.apiUrl}/api/ai/score-lead`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(leadData)
            });

            if (!response.ok) throw new Error('AI scoring unavailable');
            
            const result = await response.json();
            
            if (result.success) {
                console.log(`🤖 AI Analysis:`, {
                    score: result.ai_score,
                    priority: result.priority,
                    probability: result.conversion_probability
                });
                return result;
            }
        } catch (error) {
            console.log('🔄 AI scoring failed, using standard processing');
        }
        
        return null;
    }

    async submitEnhancedLead(data, aiResult) {
        // Prepare enhanced data for submission
        const enhancedData = {
            ...data,
            ai_score: aiResult?.ai_score || 100,
            priority: aiResult?.priority || 'P3',
            conversion_probability: aiResult?.conversion_probability || 0.5,
            ai_recommendations: aiResult?.recommendations || []
        };

        // Submit to your existing lead capture system
        const response = await fetch('/api/lead-capture', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(enhancedData)
        });

        return response.json();
    }

    showAIEnhancedResponse(aiResult) {
        if (!aiResult) {
            this.showStandardThankYou();
            return;
        }

        // High priority leads get special treatment
        if (aiResult.priority === 'P1' || aiResult.priority === 'P2') {
            this.showPriorityResponse(aiResult);
        } else {
            this.showEnhancedThankYou(aiResult);
        }

        // Track AI-enhanced conversion
        this.trackAIConversion(aiResult);
    }

    showPriorityResponse(aiResult) {
        const modal = document.createElement('div');
        modal.className = 'priority-response-modal';
        modal.innerHTML = `
            <div class="priority-modal-content">
                <div class="priority-header ${aiResult.priority.toLowerCase()}">
                    <div class="priority-badge">${aiResult.priority} PRIORITY</div>
                    <h2>🚨 Immediate Foreclosure Assistance</h2>
                    <p>Our AI analysis indicates you need urgent attention</p>
                </div>
                
                <div class="ai-analysis">
                    <div class="score-circle">
                        <div class="score-number">${aiResult.ai_score}</div>
                        <div class="score-label">Urgency Score</div>
                    </div>
                    
                    <div class="ai-insights">
                        <h4>🤖 AI Recommendations:</h4>
                        <ul class="recommendations-list">
                            ${aiResult.recommendations.slice(0, 3).map(rec => 
                                `<li>${rec}</li>`
                            ).join('')}
                        </ul>
                    </div>
                </div>
                
                <div class="priority-actions">
                    <button class="emergency-call" onclick="window.open('tel:9495655285')">
                        📞 Call Now - Priority Line
                        <small>Available 24/7 for emergencies</small>
                    </button>
                    
                    <button class="priority-consultation" onclick="foreclosureAI.schedulePriorityConsultation()">
                        ⚡ Emergency Consultation
                        <small>Response within ${aiResult.response_time}</small>
                    </button>
                </div>
                
                <div class="confidence-display">
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${(aiResult.conversion_probability * 100)}%"></div>
                    </div>
                    <small>AI Confidence: ${(aiResult.conversion_probability * 100).toFixed(1)}% match for our services</small>
                </div>
                
                <button class="close-modal" onclick="this.closest('.priority-response-modal').remove()">×</button>
            </div>
        `;

        document.body.appendChild(modal);

        // Track priority response shown
        if (typeof gtag !== 'undefined') {
            gtag('event', 'priority_response_shown', {
                'event_category': 'AI Conversion',
                'ai_score': aiResult.ai_score,
                'priority': aiResult.priority
            });
        }
    }

    // Property analysis integration
    addPropertyAnalysis() {
        const addressField = document.querySelector('[name="property_address"]');
        if (!addressField) return;

        addressField.addEventListener('blur', () => {
            if (addressField.value.length > 10) {
                this.analyzeProperty(addressField.value);
            }
        });
    }

    async analyzeProperty(address) {
        if (this.fallbackMode) return;

        try {
            const response = await fetch(`${this.apiUrl}/api/ai/property-analysis`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ property_address: address })
            });

            const analysis = await response.json();
            
            if (analysis.success) {
                this.displayPropertyInsights(analysis);
            }
        } catch (error) {
            console.log('Property analysis unavailable');
        }
    }

    displayPropertyInsights(analysis) {
        // Remove existing insights
        const existing = document.querySelector('.property-insights');
        if (existing) existing.remove();

        const insights = document.createElement('div');
        insights.className = 'property-insights';
        insights.innerHTML = `
            <div class="insights-header">
                <h4>🏠 AI Property Analysis</h4>
                <span class="insights-badge">Powered by AI</span>
            </div>
            
            <div class="insights-grid">
                <div class="insight-item">
                    <span class="insight-icon">💰</span>
                    <div class="insight-content">
                        <span class="insight-label">Estimated Value</span>
                        <span class="insight-value">$${analysis.estimated_value.toLocaleString()}</span>
                    </div>
                </div>
                
                <div class="insight-item">
                    <span class="insight-icon">⚠️</span>
                    <div class="insight-content">
                        <span class="insight-label">Risk Level</span>
                        <span class="insight-value risk-${analysis.risk_level.toLowerCase().replace(' ', '-')}">
                            ${analysis.risk_level}
                        </span>
                    </div>
                </div>
                
                <div class="insight-item">
                    <span class="insight-icon">📊</span>
                    <div class="insight-content">
                        <span class="insight-label">Loan-to-Value</span>
                        <span class="insight-value">${analysis.loan_to_value.toFixed(1)}%</span>
                    </div>
                </div>
            </div>
            
            <div class="ai-recommendations">
                <h5>💡 AI Recommendations:</h5>
                <ul>
                    ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        `;

        // Insert after the address field
        const addressField = document.querySelector('[name="property_address"]');
        if (addressField && addressField.closest('.form-group')) {
            addressField.closest('.form-group').insertAdjacentElement('afterend', insights);
        }
    }

    // Behavioral tracking for AI scoring
    setupBehavioralTracking() {
        this.sessionData = {
            startTime: Date.now(),
            pageViews: 1,
            scrollDepth: 0,
            formInteractions: 0,
            phoneClicks: 0,
            timeOnPage: 0,
            consultationInterest: false
        };

        // Track scroll depth
        let maxScroll = 0;
        window.addEventListener('scroll', () => {
            const scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
            maxScroll = Math.max(maxScroll, scrollPercent);
            this.sessionData.scrollDepth = maxScroll;
        });

        // Track form interactions
        document.addEventListener('focus', (e) => {
            if (e.target.matches('input, textarea, select')) {
                this.sessionData.formInteractions++;
            }
        }, true);

        // Track phone clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('a[href^="tel:"]')) {
                this.sessionData.phoneClicks++;
            }
            
            if (e.target.textContent.toLowerCase().includes('consultation')) {
                this.sessionData.consultationInterest = true;
            }
        });

        // Update time on page every 30 seconds
        setInterval(() => {
            this.sessionData.timeOnPage = Date.now() - this.sessionData.startTime;
        }, 30000);
    }

    getSessionData() {
        this.sessionData.timeOnPage = Date.now() - this.sessionData.startTime;
        return { ...this.sessionData };
    }

    getDeviceType() {
        if (window.innerWidth <= 768) return 'mobile';
        if (window.innerWidth <= 1024) return 'tablet';
        return 'desktop';
    }

    getTrafficSource() {
        const ref = document.referrer;
        if (ref.includes('google.com')) return 'google_organic';
        if (ref.includes('facebook.com')) return 'facebook';
        if (ref.includes('google.com/maps')) return 'google_my_business';
        if (ref) return 'referral';
        return 'direct';
    }

    trackAIConversion(aiResult) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'ai_enhanced_lead', {
                'event_category': 'AI Lead Scoring',
                'ai_score': aiResult.ai_score,
                'priority': aiResult.priority,
                'conversion_probability': aiResult.conversion_probability
            });
        }
    }

    // Utility methods
    showFormLoading(form) {
        const submitBtn = form.querySelector('[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Processing with AI...';
        }
    }

    showStandardThankYou() {
        window.location.href = '/thank-you.html';
    }

    showEnhancedThankYou(aiResult) {
        window.location.href = `/thank-you.html?score=${aiResult.ai_score}&priority=${aiResult.priority}`;
    }

    submitStandardForm(data) {
        // Fallback submission without AI
        window.location.href = '/thank-you.html';
    }

    schedulePriorityConsultation() {
        // Integration with calendar booking system
        window.open('tel:9495655285');
    }

    showPriorityForm() {
        // Show simplified priority form for emergencies
        const form = document.createElement('div');
        form.className = 'priority-form-modal';
        form.innerHTML = `
            <div class="priority-form-content">
                <h3>🚨 Emergency Consultation Request</h3>
                <form class="emergency-form">
                    <input type="text" name="name" placeholder="Your Name" required>
                    <input type="tel" name="phone" placeholder="Phone Number" required>
                    <textarea name="emergency_situation" placeholder="Describe your emergency situation..." required></textarea>
                    <button type="submit">📞 Request Emergency Call</button>
                </form>
                <button class="close-modal" onclick="this.closest('.priority-form-modal').remove()">×</button>
            </div>
        `;
        document.body.appendChild(form);
    }
}

// Initialize AI when page loads
let foreclosureAI;
document.addEventListener('DOMContentLoaded', () => {
    foreclosureAI = new ForeclosureAI();
});

// CSS Styles for AI features
const aiStyles = `
<style>
.emergency-assistance {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    animation: fadeIn 0.3s ease;
}

.emergency-content {
    background: white;
    border-radius: 12px;
    padding: 30px;
    max-width: 500px;
    width: 90%;
    position: relative;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}

.emergency-header {
    text-align: center;
    margin-bottom: 20px;
    padding: 15px;
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
    color: white;
    border-radius: 8px;
}

.emergency-icon {
    font-size: 24px;
    display: block;
    margin-bottom: 8px;
}

.emergency-call-btn, .priority-form-btn {
    width: 100%;
    padding: 15px;
    margin: 10px 0;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    font-size: 16px;
}

.emergency-call-btn {
    background: #dc2626;
    color: white;
}

.priority-form-btn {
    background: #1e40af;
    color: white;
}

.priority-response-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
}

.priority-modal-content {
    background: white;
    border-radius: 16px;
    padding: 40px;
    max-width: 600px;
    width: 90%;
    position: relative;
    box-shadow: 0 25px 50px rgba(0,0,0,0.4);
}

.priority-header {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    border-radius: 12px;
    color: white;
}

.priority-header.p1 {
    background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
}

.priority-header.p2 {
    background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
}

.priority-badge {
    display: inline-block;
    padding: 6px 12px;
    background: rgba(255,255,255,0.2);
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 10px;
}

.ai-analysis {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 30px;
    margin: 30px 0;
    align-items: start;
}

.score-circle {
    text-align: center;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 12px;
    min-width: 120px;
}

.score-number {
    display: block;
    font-size: 36px;
    font-weight: 700;
    color: #dc2626;
    line-height: 1;
}

.score-label {
    font-size: 12px;
    color: #6b7280;
    margin-top: 5px;
}

.recommendations-list {
    list-style: none;
    padding: 0;
}

.recommendations-list li {
    padding: 8px 0;
    border-bottom: 1px solid #f3f4f6;
    position: relative;
    padding-left: 20px;
}

.recommendations-list li:before {
    content: "🎯";
    position: absolute;
    left: 0;
}

.priority-actions {
    display: grid;
    gap: 15px;
    margin: 30px 0;
}

.emergency-call, .priority-consultation {
    padding: 18px 24px;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    font-size: 16px;
    text-align: left;
    transition: transform 0.2s ease;
}

.emergency-call {
    background: #dc2626;
    color: white;
}

.priority-consultation {
    background: #1e40af;
    color: white;
}

.emergency-call:hover, .priority-consultation:hover {
    transform: translateY(-2px);
}

.emergency-call small, .priority-consultation small {
    display: block;
    opacity: 0.8;
    font-weight: 400;
    margin-top: 4px;
}

.confidence-display {
    margin: 20px 0;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

.confidence-bar {
    width: 100%;
    height: 8px;
    background: #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 8px;
}

.confidence-fill {
    height: 100%;
    background: linear-gradient(90deg, #10b981 0%, #059669 100%);
    transition: width 0.5s ease;
}

.property-insights {
    margin: 20px 0;
    padding: 24px;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-radius: 12px;
    border-left: 4px solid #1e40af;
}

.insights-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.insights-badge {
    background: #1e40af;
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
}

.insights-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.insight-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 15px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.insight-icon {
    font-size: 20px;
}

.insight-content {
    flex: 1;
}

.insight-label {
    display: block;
    font-size: 12px;
    color: #6b7280;
    margin-bottom: 4px;
}

.insight-value {
    display: block;
    font-size: 16px;
    font-weight: 600;
    color: #1e40af;
}

.close-modal, .close-emergency {
    position: absolute;
    top: 15px;
    right: 15px;
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #6b7280;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
}

.close-modal:hover, .close-emergency:hover {
    background: rgba(0,0,0,0.1);
}

.spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid #f3f4f6;
    border-top: 2px solid #1e40af;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
}

@media (max-width: 768px) {
    .ai-analysis {
        grid-template-columns: 1fr;
        text-align: center;
    }
    
    .insights-grid {
        grid-template-columns: 1fr;
    }
    
    .priority-modal-content, .emergency-content {
        padding: 20px;
        margin: 20px;
    }
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', aiStyles);