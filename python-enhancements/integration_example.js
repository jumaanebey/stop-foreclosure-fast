/**
 * Python AI Integration Examples for Virtual Foreclosure Website
 * Add these functions to your existing js/script.js
 */

// Enhanced form submission with AI scoring
async function handleFormSubmissionWithAI(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Add session tracking data
    data.session_data = getSessionTrackingData();
    data.form_type = 'contact';
    data.lead_source = getTrafficSource();
    data.device_type = getDeviceType();
    
    try {
        // Get AI enhancement for the lead
        const aiResult = await enhanceLeadWithAI(data);
        
        // Submit with AI enhancements
        const response = await fetch('/api/lead-capture', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...data,
                ai_score: aiResult?.ai_score || 100,
                priority: aiResult?.priority || 'P3',
                ai_recommendations: aiResult?.recommendations || []
            })
        });
        
        const result = await response.json();
        
        // Handle priority leads with special treatment
        if (aiResult && (aiResult.priority === 'P1' || aiResult.priority === 'P2')) {
            showPriorityResponse(aiResult);
        } else {
            showStandardThankYou();
        }
        
        // Track AI-enhanced conversion
        trackAIConversion(data, aiResult);
        
    } catch (error) {
        console.error('AI enhancement error:', error);
        // Fallback to standard submission
        submitStandardForm(data);
    }
}

// Core AI enhancement function
async function enhanceLeadWithAI(leadData) {
    try {
        const response = await fetch('/api/ai/score-lead', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(leadData)
        });
        
        if (!response.ok) {
            throw new Error('AI service unavailable');
        }
        
        const aiResult = await response.json();
        
        if (aiResult.success) {
            console.log(`🤖 AI Enhancement:`, {
                score: aiResult.ai_score,
                priority: aiResult.priority,
                conversion_probability: aiResult.conversion_probability,
                recommendations: aiResult.recommendations
            });
            
            return aiResult;
        }
        
    } catch (error) {
        console.log('🔄 AI enhancement unavailable, using standard processing');
        return null;
    }
}

// Real-time urgency analysis
async function analyzeUrgencyInRealTime(situationText) {
    if (!situationText || situationText.length < 10) return;
    
    try {
        const response = await fetch('/api/ai/analyze-urgency', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                situation: situationText,
                timestamp: new Date().toISOString()
            })
        });
        
        const urgencyResult = await response.json();
        
        if (urgencyResult.success && urgencyResult.escalate) {
            // Show emergency assistance popup
            showEmergencyAssistancePopup(urgencyResult);
            
            // Track emergency situation
            gtag('event', 'emergency_situation_detected', {
                'event_category': 'AI Analysis',
                'urgency_level': urgencyResult.urgency_level,
                'keywords': urgencyResult.keywords_detected.join(', ')
            });
        }
        
    } catch (error) {
        console.log('Urgency analysis unavailable');
    }
}

// Property analysis integration
async function analyzeProperty(propertyAddress, loanAmount = 0, income = 0) {
    try {
        const response = await fetch('/api/ai/property-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                property_address: propertyAddress,
                loan_amount: parseFloat(loanAmount) || 0,
                income: parseFloat(income) || 0
            })
        });
        
        const analysis = await response.json();
        
        if (analysis.success) {
            displayPropertyInsights(analysis);
            return analysis;
        }
        
    } catch (error) {
        console.log('Property analysis unavailable');
    }
}

// Smart content personalization
async function personalizeContentForVisitor(leadData) {
    try {
        const response = await fetch('/api/ai/personalize-content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lead_data: leadData,
                content_type: 'welcome'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update page content with personalized messaging
            updatePersonalizedContent(result.personalized_content);
            
            // Store optimal timing for future communications
            sessionStorage.setItem('optimalContactTime', 
                JSON.stringify(result.optimal_send_time));
        }
        
    } catch (error) {
        console.log('Content personalization unavailable');
    }
}

// Enhanced popup for priority leads
function showPriorityResponse(aiResult) {
    const popup = document.createElement('div');
    popup.className = 'priority-popup';
    popup.innerHTML = `
        <div class="priority-popup-content">
            <div class="priority-header ${aiResult.priority.toLowerCase()}">
                <h3>🚨 PRIORITY FORECLOSURE ASSISTANCE</h3>
                <p>Our AI analysis indicates you need immediate attention</p>
            </div>
            
            <div class="ai-insights">
                <div class="score-display">
                    <span class="score-number">${aiResult.ai_score}</span>
                    <span class="score-label">AI Urgency Score</span>
                </div>
                
                <div class="recommendations">
                    <h4>Immediate Next Steps:</h4>
                    <ul>
                        ${aiResult.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
            
            <div class="priority-actions">
                <button class="emergency-call-btn" onclick="window.open('tel:9493284811')">
                    📞 Call Now - Emergency Line
                </button>
                <button class="priority-consultation-btn" onclick="schedulePriorityConsultation()">
                    ⚡ Priority Consultation
                </button>
            </div>
            
            <button class="close-popup" onclick="closePriorityPopup()">&times;</button>
        </div>
    `;
    
    document.body.appendChild(popup);
    
    // Track priority popup display
    gtag('event', 'priority_popup_shown', {
        'event_category': 'AI Conversion',
        'ai_score': aiResult.ai_score,
        'priority_level': aiResult.priority
    });
}

// Emergency assistance popup
function showEmergencyAssistancePopup(urgencyResult) {
    if (document.querySelector('.emergency-popup')) return; // Prevent duplicates
    
    const popup = document.createElement('div');
    popup.className = 'emergency-popup';
    popup.innerHTML = `
        <div class="emergency-popup-content">
            <div class="emergency-header">
                <h3>🚨 FORECLOSURE EMERGENCY DETECTED</h3>
                <p>Our AI detected urgent keywords in your situation</p>
            </div>
            
            <div class="urgency-details">
                <div class="urgency-level ${urgencyResult.urgency_level}">
                    Urgency Level: ${urgencyResult.urgency_level.toUpperCase()}
                </div>
                <div class="action-required">
                    ${urgencyResult.action_required}
                </div>
            </div>
            
            <div class="emergency-actions">
                <button class="emergency-call-btn" onclick="window.open('tel:9493284811')">
                    📞 CALL EMERGENCY LINE NOW
                </button>
                <button class="emergency-form-btn" onclick="showEmergencyForm()">
                    ⚡ Emergency Consultation Request
                </button>
            </div>
            
            <div class="emergency-note">
                <small>Available 24/7 for foreclosure emergencies across California</small>
            </div>
        </div>
    `;
    
    document.body.appendChild(popup);
    
    // Auto-remove after 30 seconds if no action
    setTimeout(() => {
        if (popup.parentNode) {
            popup.remove();
        }
    }, 30000);
}

// Property insights display
function displayPropertyInsights(analysis) {
    const insights = document.createElement('div');
    insights.className = 'property-insights';
    insights.innerHTML = `
        <div class="insights-header">
            <h4>🏠 AI Property Analysis</h4>
        </div>
        
        <div class="insights-grid">
            <div class="insight-item">
                <span class="insight-label">Estimated Value</span>
                <span class="insight-value">$${analysis.estimated_value.toLocaleString()}</span>
            </div>
            
            <div class="insight-item">
                <span class="insight-label">Risk Level</span>
                <span class="insight-value risk-${analysis.risk_level.toLowerCase().replace(' ', '-')}">
                    ${analysis.risk_level}
                </span>
            </div>
            
            <div class="insight-item">
                <span class="insight-label">Loan-to-Value</span>
                <span class="insight-value">${analysis.loan_to_value.toFixed(1)}%</span>
            </div>
        </div>
        
        <div class="ai-recommendations">
            <h5>AI Recommendations:</h5>
            <ul>
                ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        </div>
    `;
    
    // Insert after property address field if it exists
    const addressField = document.querySelector('[name="property_address"]');
    if (addressField && addressField.parentNode) {
        addressField.parentNode.insertBefore(insights, addressField.nextSibling);
    }
}

// Track AI-enhanced conversions
function trackAIConversion(leadData, aiResult) {
    if (!aiResult) return;
    
    gtag('event', 'ai_enhanced_conversion', {
        'event_category': 'AI Lead Scoring',
        'ai_score': aiResult.ai_score,
        'priority': aiResult.priority,
        'conversion_probability': aiResult.conversion_probability,
        'county': leadData.county || 'unknown',
        'device_type': leadData.device_type || 'unknown',
        'lead_source': leadData.lead_source || 'direct'
    });
    
    // Track to Facebook Pixel if available
    if (typeof fbq !== 'undefined') {
        fbq('trackCustom', 'AIEnhancedLead', {
            score: aiResult.ai_score,
            priority: aiResult.priority,
            county: leadData.county
        });
    }
}

// Real-time form enhancement
document.addEventListener('DOMContentLoaded', function() {
    // Add AI analysis to situation textarea
    const situationField = document.querySelector('[name="situation"]');
    if (situationField) {
        let timeout;
        situationField.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                analyzeUrgencyInRealTime(this.value);
            }, 2000); // Analyze after 2 seconds of no typing
        });
    }
    
    // Add property analysis to address field
    const addressField = document.querySelector('[name="property_address"]');
    if (addressField) {
        addressField.addEventListener('blur', function() {
            if (this.value.length > 10) {
                analyzeProperty(this.value);
            }
        });
    }
    
    // Enhance all forms with AI
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmissionWithAI(this);
        });
    });
});

// AI Dashboard Integration
function openAIDashboard() {
    window.open('/python-enhancements/dashboard.html', '_blank', 
        'width=1200,height=800,scrollbars=yes,resizable=yes');
}

// Add AI dashboard link to admin area
if (window.location.search.includes('admin=true')) {
    const dashboardLink = document.createElement('a');
    dashboardLink.href = '#';
    dashboardLink.textContent = '🤖 AI Dashboard';
    dashboardLink.onclick = openAIDashboard;
    dashboardLink.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #1e40af;
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    document.body.appendChild(dashboardLink);
}

// CSS for AI-enhanced popups
const aiStyles = document.createElement('style');
aiStyles.textContent = `
    .priority-popup, .emergency-popup {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeIn 0.3s ease;
    }
    
    .priority-popup-content, .emergency-popup-content {
        background: white;
        border-radius: 12px;
        padding: 30px;
        max-width: 500px;
        width: 90%;
        position: relative;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }
    
    .priority-header, .emergency-header {
        text-align: center;
        margin-bottom: 20px;
        padding: 15px;
        border-radius: 8px;
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white;
    }
    
    .score-display {
        text-align: center;
        margin: 20px 0;
    }
    
    .score-number {
        display: block;
        font-size: 48px;
        font-weight: 700;
        color: #dc2626;
    }
    
    .emergency-call-btn, .priority-consultation-btn {
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
    
    .priority-consultation-btn {
        background: #1e40af;
        color: white;
    }
    
    .property-insights {
        margin: 20px 0;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 4px solid #1e40af;
    }
    
    .insights-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
        margin: 15px 0;
    }
    
    .insight-item {
        text-align: center;
    }
    
    .insight-label {
        display: block;
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 4px;
    }
    
    .insight-value {
        display: block;
        font-size: 18px;
        font-weight: 600;
        color: #1e40af;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }
`;
document.head.appendChild(aiStyles);