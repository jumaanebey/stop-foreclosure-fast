# Advanced Lead Scoring and Qualification System

## Intelligent Lead Qualification for Virtual Foreclosure Business

### Lead Scoring Matrix Overview

#### Multi-Factor Scoring Algorithm
The lead scoring system evaluates potential clients across multiple dimensions to prioritize follow-up efforts and customize service delivery for maximum conversion rates.

**Total Score Range:** 0-500 points
**Qualification Thresholds:**
- **500-400 points:** HOT LEAD (Immediate priority)
- **399-300 points:** WARM LEAD (High priority)  
- **299-200 points:** QUALIFIED LEAD (Medium priority)
- **199-100 points:** COLD LEAD (Low priority)
- **99-0 points:** UNQUALIFIED (Archive/nurture only)

### Scoring Categories and Weights

#### 1. Urgency & Timeline Scoring (Weight: 40% - Max 200 points)
```javascript
const urgencyScoring = {
    // Immediate foreclosure threat
    'auction_within_7_days': 200,
    'auction_within_14_days': 180,
    'auction_within_30_days': 160,
    
    // Notice status
    'notice_of_sale_received': 140,
    'notice_of_default_received': 120,
    'notice_of_default_imminent': 100,
    
    // Payment status
    'missed_4_plus_payments': 80,
    'missed_2_3_payments': 60,
    'missed_1_payment': 40,
    'behind_but_current': 20,
    
    // Planning ahead
    'exploring_options': 10,
    'general_inquiry': 5
};

function calculateUrgencyScore(leadData) {
    let score = 0;
    
    // Primary urgency factor
    score += urgencyScoring[leadData.urgency_level] || 0;
    
    // Timeline multipliers
    if (leadData.auction_date) {
        const daysToAuction = calculateDaysToDate(leadData.auction_date);
        if (daysToAuction <= 7) score *= 1.2;
        else if (daysToAuction <= 14) score *= 1.1;
    }
    
    // Payment delinquency depth
    if (leadData.months_behind) {
        const monthsMultiplier = Math.min(leadData.months_behind * 0.1, 0.5);
        score *= (1 + monthsMultiplier);
    }
    
    return Math.min(score, 200);
}
```

#### 2. Financial Capacity Scoring (Weight: 25% - Max 125 points)
```javascript
const financialCapacityScoring = {
    // Income stability
    stable_employment: 30,
    unstable_employment: 15,
    unemployed: 0,
    retired_fixed_income: 25,
    self_employed: 20,
    
    // Property value (estimated)
    property_value_over_1M: 40,
    property_value_500K_1M: 30,
    property_value_300K_500K: 20,
    property_value_under_300K: 10,
    
    // Available resources
    has_savings: 25,
    has_401k: 20,
    has_family_support: 15,
    no_additional_resources: 0,
    
    // Debt-to-income ratio
    dti_under_30: 10,
    dti_30_45: 5,
    dti_over_45: 0
};

function calculateFinancialScore(leadData) {
    let score = 0;
    
    // Employment status
    score += financialCapacityScoring[leadData.employment_status] || 0;
    
    // Property value estimation
    if (leadData.property_value || leadData.property_address) {
        const estimatedValue = leadData.property_value || 
                              estimatePropertyValue(leadData.property_address);
        
        if (estimatedValue > 1000000) score += 40;
        else if (estimatedValue > 500000) score += 30;
        else if (estimatedValue > 300000) score += 20;
        else score += 10;
    }
    
    // Financial resources
    if (leadData.has_savings) score += 25;
    if (leadData.has_401k) score += 20;
    if (leadData.family_support) score += 15;
    
    // Debt-to-income ratio
    if (leadData.monthly_income && leadData.total_debt) {
        const dti = (leadData.total_debt / leadData.monthly_income) * 100;
        if (dti < 30) score += 10;
        else if (dti < 45) score += 5;
    }
    
    return Math.min(score, 125);
}
```

#### 3. Engagement & Intent Scoring (Weight: 20% - Max 100 points)
```javascript
const engagementScoring = {
    // Website behavior
    visited_consultation_page: 20,
    downloaded_resources: 15,
    viewed_multiple_pages: 10,
    spent_over_5_minutes: 10,
    
    // Form completion
    completed_full_form: 25,
    provided_phone_number: 15,
    provided_detailed_situation: 10,
    
    // Communication response
    answered_initial_call: 20,
    responded_to_email: 10,
    requested_callback: 15,
    no_response_24_hours: -10,
    
    // Consultation interest
    requested_virtual_consultation: 30,
    preferred_immediate_consultation: 25,
    flexible_scheduling: 15,
    hesitant_about_consultation: 5
};

function calculateEngagementScore(leadData, behaviorData) {
    let score = 0;
    
    // Website engagement
    if (behaviorData.pages_visited > 3) score += 10;
    if (behaviorData.time_on_site > 300) score += 10; // 5+ minutes
    if (behaviorData.consultation_page_viewed) score += 20;
    if (behaviorData.resources_downloaded) score += 15;
    
    // Form completion quality
    const formCompleteness = calculateFormCompleteness(leadData);
    score += formCompleteness * 25; // 0-1 ratio
    
    if (leadData.phone_provided) score += 15;
    if (leadData.detailed_situation) score += 10;
    
    // Communication responsiveness
    if (behaviorData.call_answered) score += 20;
    if (behaviorData.email_responded) score += 10;
    if (behaviorData.callback_requested) score += 15;
    
    // Consultation interest
    if (leadData.consultation_requested) score += 30;
    if (leadData.preferred_timing === 'immediate') score += 25;
    
    return Math.min(score, 100);
}
```

#### 4. Geographic & Market Factors (Weight: 10% - Max 50 points)
```javascript
const geographicScoring = {
    // High-value markets
    'Los Angeles': 50,
    'Orange County': 45,
    'San Francisco': 50,
    'San Mateo': 45,
    'Santa Clara': 45,
    'Marin': 40,
    'San Diego': 40,
    
    // Medium-value markets
    'Alameda': 35,
    'Contra Costa': 35,
    'Riverside': 30,
    'San Bernardino': 30,
    'Ventura': 35,
    'Santa Barbara': 35,
    
    // Emerging markets
    'Sacramento': 25,
    'Fresno': 20,
    'Kern': 20,
    'Tulare': 15,
    
    // Rural/remote markets
    'Imperial': 10,
    'Mono': 10,
    'Alpine': 5
};

function calculateGeographicScore(leadData) {
    let score = 0;
    
    // County-based scoring
    score += geographicScoring[leadData.county] || 15; // Default for unlisted counties
    
    // Urban vs rural adjustment
    if (leadData.city_type === 'urban') score *= 1.1;
    else if (leadData.city_type === 'rural') score *= 0.9;
    
    // Market conditions
    const marketData = getCurrentMarketConditions(leadData.county);
    if (marketData.foreclosure_rate > 0.05) score *= 1.2; // High foreclosure rate
    if (marketData.property_appreciation > 0.1) score *= 1.1; // Rising values
    
    return Math.min(score, 50);
}
```

#### 5. Lead Source Quality (Weight: 5% - Max 25 points)
```javascript
const sourceQualityScoring = {
    // High-intent sources
    'google_organic_foreclosure': 25,
    'google_my_business': 23,
    'referral_from_client': 25,
    'referral_from_professional': 22,
    
    // Medium-intent sources
    'google_ads_foreclosure': 20,
    'facebook_ads_targeted': 18,
    'linkedin_organic': 16,
    'directory_listing': 15,
    
    // Lower-intent sources
    'social_media_general': 10,
    'content_marketing': 12,
    'email_campaign': 8,
    'cold_outreach': 5
};

function calculateSourceScore(leadData) {
    let score = sourceQualityScoring[leadData.lead_source] || 10;
    
    // UTM campaign quality
    if (leadData.utm_campaign) {
        if (leadData.utm_campaign.includes('emergency')) score += 5;
        if (leadData.utm_campaign.includes('urgent')) score += 3;
    }
    
    // Referrer quality
    if (leadData.referrer && leadData.referrer.includes('foreclosure')) score += 3;
    
    return Math.min(score, 25);
}
```

### Advanced Qualification Criteria

#### Hot Lead Qualification (400+ points)
```javascript
function qualifyHotLead(leadScore, leadData) {
    const qualificationCriteria = {
        minimum_score: 400,
        required_criteria: [
            'urgency_level_critical',     // Auction within 30 days OR Notice of Sale
            'contact_information_complete', // Phone and email provided
            'situation_described',        // Basic foreclosure details provided
            'consultation_interest'       // Expressed interest in virtual consultation
        ],
        bonus_criteria: [
            'immediate_availability',     // Can meet within 24 hours
            'financial_capacity_indicated', // Has some resources available
            'high_value_property',       // Property value > $500K
            'referred_by_professional'   // Attorney, CPA, realtor referral
        ]
    };
    
    if (leadScore < qualificationCriteria.minimum_score) return false;
    
    // Check required criteria
    const requiredMet = qualificationCriteria.required_criteria.every(criterion => {
        return evaluateCriterion(criterion, leadData);
    });
    
    if (!requiredMet) return false;
    
    // Count bonus criteria
    const bonusMet = qualificationCriteria.bonus_criteria.filter(criterion => {
        return evaluateCriterion(criterion, leadData);
    }).length;
    
    return {
        qualified: true,
        score: leadScore,
        required_criteria_met: qualificationCriteria.required_criteria.length,
        bonus_criteria_met: bonusMet,
        priority: 'immediate',
        recommended_action: 'emergency_consultation_outreach'
    };
}
```

#### Lead Routing Logic
```javascript
class LeadRoutingEngine {
    constructor() {
        this.agents = this.loadAgentCapabilities();
        this.routingRules = this.initializeRoutingRules();
    }
    
    async routeLead(leadData, leadScore) {
        const qualification = this.qualifyLead(leadScore, leadData);
        const routingDecision = await this.determineRouting(leadData, qualification);
        
        return {
            assigned_agent: routingDecision.agent,
            priority_level: routingDecision.priority,
            response_timeline: routingDecision.timeline,
            recommended_actions: routingDecision.actions,
            consultation_type: routingDecision.consultationType,
            special_instructions: routingDecision.instructions
        };
    }
    
    async determineRouting(leadData, qualification) {
        let routingDecision = {
            agent: null,
            priority: 'medium',
            timeline: '24_hours',
            actions: [],
            consultationType: 'standard_virtual',
            instructions: []
        };
        
        // Emergency routing (500-450 points)
        if (qualification.score >= 450) {
            routingDecision = {
                agent: await this.getEmergencyAgent(),
                priority: 'emergency',
                timeline: '1_hour',
                actions: ['immediate_call', 'emergency_email', 'text_if_available'],
                consultationType: 'emergency_virtual',
                instructions: ['Same-day consultation required', 'Multiple contact attempts authorized']
            };
        }
        
        // Hot lead routing (400-449 points)
        else if (qualification.score >= 400) {
            routingDecision = {
                agent: await this.getTopAgent(leadData.county),
                priority: 'high',
                timeline: '4_hours',
                actions: ['priority_call', 'urgent_email', 'consultation_booking'],
                consultationType: 'priority_virtual',
                instructions: ['Consultation within 24 hours', 'Senior agent assignment']
            };
        }
        
        // Warm lead routing (300-399 points)
        else if (qualification.score >= 300) {
            routingDecision = {
                agent: await this.getAvailableAgent(leadData.county),
                priority: 'medium',
                timeline: '8_hours',
                actions: ['standard_call', 'welcome_email', 'resource_sharing'],
                consultationType: 'standard_virtual',
                instructions: ['Standard consultation process', 'Full needs assessment']
            };
        }
        
        // Qualified lead routing (200-299 points)
        else if (qualification.score >= 200) {
            routingDecision = {
                agent: await this.getJuniorAgent(),
                priority: 'low',
                timeline: '24_hours',
                actions: ['email_first', 'educational_content', 'nurture_sequence'],
                consultationType: 'educational_virtual',
                instructions: ['Focus on education', 'Build trust and urgency']
            };
        }
        
        // Cold lead routing (100-199 points)
        else if (qualification.score >= 100) {
            routingDecision = {
                agent: 'automation_system',
                priority: 'low',
                timeline: '72_hours',
                actions: ['email_nurture_sequence', 'content_delivery', 'retargeting'],
                consultationType: 'automated_nurture',
                instructions: ['Automated follow-up', 'Monitor for engagement increase']
            };
        }
        
        return routingDecision;
    }
}
```

### Real-Time Lead Scoring Implementation

#### Dynamic Scoring Updates
```javascript
class RealTimeLeadScoring {
    constructor(leadId) {
        this.leadId = leadId;
        this.scoreHistory = [];
        this.behaviorTracking = new BehaviorTracker(leadId);
    }
    
    async updateScore(triggerEvent, eventData) {
        const currentScore = await this.getCurrentScore();
        const scoreChange = this.calculateScoreChange(triggerEvent, eventData);
        const newScore = Math.max(0, Math.min(500, currentScore + scoreChange));
        
        // Log score change
        const scoreUpdate = {
            timestamp: new Date().toISOString(),
            previous_score: currentScore,
            new_score: newScore,
            change: scoreChange,
            trigger: triggerEvent,
            event_data: eventData
        };
        
        this.scoreHistory.push(scoreUpdate);
        
        // Update in CRM
        await this.updateCRMScore(newScore, scoreUpdate);
        
        // Check for routing changes
        await this.checkRoutingChange(currentScore, newScore);
        
        // Trigger automated actions if threshold crossed
        await this.triggerThresholdActions(currentScore, newScore);
        
        return scoreUpdate;
    }
    
    calculateScoreChange(triggerEvent, eventData) {
        const scoringRules = {
            // Positive engagement
            'email_opened': 5,
            'email_clicked': 10,
            'phone_answered': 25,
            'consultation_booked': 50,
            'documents_uploaded': 30,
            'referral_provided': 40,
            
            // Urgency increases
            'auction_date_updated': (data) => {
                const daysToAuction = calculateDaysToDate(data.auction_date);
                if (daysToAuction <= 7) return 50;
                if (daysToAuction <= 14) return 30;
                if (daysToAuction <= 30) return 20;
                return 0;
            },
            
            // Negative engagement
            'email_unsubscribed': -50,
            'call_declined': -15,
            'consultation_no_show': -40,
            'no_response_72_hours': -20,
            
            // Financial improvements
            'income_verified': 20,
            'resources_confirmed': 25,
            'loan_modification_started': 35,
            
            // Competitive behavior
            'competitor_consultation': -30,
            'solution_found_elsewhere': -100
        };
        
        const rule = scoringRules[triggerEvent];
        
        if (typeof rule === 'function') {
            return rule(eventData);
        } else if (typeof rule === 'number') {
            return rule;
        }
        
        return 0;
    }
    
    async checkRoutingChange(oldScore, newScore) {
        const oldQualification = this.getQualificationTier(oldScore);
        const newQualification = this.getQualificationTier(newScore);
        
        if (oldQualification !== newQualification) {
            // Re-route the lead
            const newRouting = await this.leadRouter.routeLead(
                await this.getLeadData(), 
                newScore
            );
            
            await this.implementRoutingChange(newRouting);
            
            // Notify stakeholders
            await this.notifyRoutingChange(oldQualification, newQualification, newRouting);
        }
    }
}
```

### Lead Qualification Dashboard

#### Real-Time Qualification Interface
```javascript
class QualificationDashboard {
    constructor() {
        this.dashboardElement = document.getElementById('qualification-dashboard');
        this.filterSettings = this.initializeFilters();
        this.refreshInterval = 30000; // 30 seconds
    }
    
    renderDashboard() {
        const dashboardHTML = `
            <div class="qualification-dashboard">
                <div class="dashboard-header">
                    <h2>Lead Qualification Dashboard</h2>
                    <div class="real-time-indicator">
                        <span class="status-dot"></span> Live Updates
                    </div>
                </div>
                
                <div class="qualification-summary">
                    <div class="score-ranges">
                        <div class="score-range hot">
                            <h3>Hot Leads</h3>
                            <div class="count" id="hot-count">0</div>
                            <div class="subtitle">400+ points</div>
                        </div>
                        <div class="score-range warm">
                            <h3>Warm Leads</h3>
                            <div class="count" id="warm-count">0</div>
                            <div class="subtitle">300-399 points</div>
                        </div>
                        <div class="score-range qualified">
                            <h3>Qualified</h3>
                            <div class="count" id="qualified-count">0</div>
                            <div class="subtitle">200-299 points</div>
                        </div>
                        <div class="score-range cold">
                            <h3>Nurture</h3>
                            <div class="count" id="cold-count">0</div>
                            <div class="subtitle">100-199 points</div>
                        </div>
                    </div>
                </div>
                
                <div class="lead-pipeline">
                    <div class="pipeline-filters">
                        <select id="urgency-filter">
                            <option value="">All Urgency Levels</option>
                            <option value="emergency">Emergency</option>
                            <option value="urgent">Urgent</option>
                            <option value="moderate">Moderate</option>
                            <option value="low">Low</option>
                        </select>
                        
                        <select id="county-filter">
                            <option value="">All Counties</option>
                            <option value="Los Angeles">Los Angeles</option>
                            <option value="Orange">Orange</option>
                            <option value="San Diego">San Diego</option>
                            <option value="Riverside">Riverside</option>
                        </select>
                        
                        <select id="source-filter">
                            <option value="">All Sources</option>
                            <option value="organic">Organic Search</option>
                            <option value="gmb">Google My Business</option>
                            <option value="referral">Referral</option>
                            <option value="social">Social Media</option>
                        </select>
                    </div>
                    
                    <div class="leads-table">
                        <table id="qualified-leads-table">
                            <thead>
                                <tr>
                                    <th>Score</th>
                                    <th>Name</th>
                                    <th>County</th>
                                    <th>Urgency</th>
                                    <th>Source</th>
                                    <th>Last Activity</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="leads-table-body">
                                <!-- Dynamic content -->
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="scoring-trends">
                    <canvas id="scoring-trends-chart"></canvas>
                </div>
            </div>
        `;
        
        this.dashboardElement.innerHTML = dashboardHTML;
        this.bindEventListeners();
        this.startRealTimeUpdates();
    }
    
    async loadQualifiedLeads() {
        const leads = await fetch('/api/leads/qualified').then(r => r.json());
        return leads.sort((a, b) => b.score - a.score);
    }
    
    updateLeadsTable(leads) {
        const tbody = document.getElementById('leads-table-body');
        tbody.innerHTML = leads.map(lead => `
            <tr class="lead-row ${this.getScoreClass(lead.score)}">
                <td>
                    <div class="score-badge ${this.getScoreClass(lead.score)}">
                        ${lead.score}
                    </div>
                </td>
                <td>
                    <div class="lead-name">
                        <strong>${lead.first_name} ${lead.last_name}</strong>
                        <div class="lead-contact">${lead.email}</div>
                    </div>
                </td>
                <td>${lead.county}</td>
                <td>
                    <span class="urgency-badge ${lead.urgency_level}">
                        ${lead.urgency_level}
                    </span>
                </td>
                <td>${lead.lead_source}</td>
                <td>${this.formatRelativeTime(lead.last_activity)}</td>
                <td>
                    <div class="action-buttons">
                        <button onclick="contactLead('${lead.id}')" class="btn-contact">
                            Contact
                        </button>
                        <button onclick="scheduleConsultation('${lead.id}')" class="btn-schedule">
                            Schedule
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
}
```

This advanced lead scoring and qualification system ensures your virtual foreclosure business prioritizes the most promising leads while providing systematic follow-up for all prospects, maximizing conversion rates and revenue potential.