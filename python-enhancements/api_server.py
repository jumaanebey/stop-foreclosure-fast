#!/usr/bin/env python3
"""
Python AI API Server for Virtual Foreclosure Business
Provides web endpoints for AI-enhanced lead scoring and automation
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
from datetime import datetime
from lead_scoring_ai import LeadScoringAPI
from email_automation import SmartEmailScheduler, EmailPersonalizationAI
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['https://myforeclosuresolution.com', 'http://localhost:3000'])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI systems
lead_ai = LeadScoringAPI()
email_scheduler = SmartEmailScheduler(
    smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    smtp_port=int(os.getenv('SMTP_PORT', '587')),
    email_user=os.getenv('EMAIL_USER', 'help@myforeclosuresolution.com'),
    email_password=os.getenv('EMAIL_PASSWORD', '')
)

@app.route('/api/ai/score-lead', methods=['POST'])
def score_lead():
    """
    AI-enhanced lead scoring endpoint
    """
    try:
        lead_data = request.json
        
        # Process lead through AI systems
        ai_result = lead_ai.process_lead(lead_data)
        
        # Determine priority level
        score = ai_result['ai_score']
        if score >= 250:
            priority = 'P1'
            response_time = '1 hour'
        elif score >= 150:
            priority = 'P2'
            response_time = '4 hours'
        elif score >= 100:
            priority = 'P3'
            response_time = '24 hours'
        else:
            priority = 'P4'
            response_time = '72 hours'
        
        # Schedule automated email
        email_scheduler.add_to_queue(lead_data, 'welcome')
        
        response = {
            'success': True,
            'ai_score': score,
            'priority': priority,
            'response_time': response_time,
            'conversion_probability': ai_result['conversion_probability'],
            'recommendations': ai_result['recommendations'][:3],  # Top 3 recommendations
            'optimal_contact_time': ai_result['optimal_email_time'],
            'suggested_approach': get_approach_strategy(score, lead_data),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Lead scored: {score} points, Priority: {priority}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error scoring lead: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'AI scoring system temporarily unavailable',
            'fallback_score': 100,
            'priority': 'P3'
        }), 500

@app.route('/api/ai/personalize-content', methods=['POST'])
def personalize_content():
    """
    Generate personalized content for leads
    """
    try:
        data = request.json
        lead_data = data.get('lead_data', {})
        content_type = data.get('content_type', 'welcome')
        
        # Generate personalized content
        personalizer = EmailPersonalizationAI()
        content = personalizer.generate_personalized_content(lead_data, content_type)
        
        # Generate subject line options
        comm_ai = lead_ai.comm_ai
        subject_lines = comm_ai.generate_personalized_subject_lines(lead_data)
        
        response = {
            'success': True,
            'personalized_content': content,
            'suggested_subjects': subject_lines[:3],
            'optimal_send_time': comm_ai.optimize_email_timing(lead_data),
            'content_type': content_type
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error personalizing content: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Content personalization temporarily unavailable'
        }), 500

@app.route('/api/ai/analyze-urgency', methods=['POST'])
def analyze_urgency():
    """
    Real-time urgency analysis for leads
    """
    try:
        lead_data = request.json
        
        # Analyze urgency using AI
        urgency_score = lead_ai.ai_scorer.analyze_lead_urgency(lead_data)
        
        # Determine urgency level
        if urgency_score >= 150:
            urgency_level = 'emergency'
            action_required = 'Immediate response required - contact within 1 hour'
            escalate = True
        elif urgency_score >= 100:
            urgency_level = 'urgent'
            action_required = 'Priority response - contact within 4 hours'
            escalate = True
        elif urgency_score >= 50:
            urgency_level = 'time_sensitive'
            action_required = 'Timely response - contact within 24 hours'
            escalate = False
        else:
            urgency_level = 'standard'
            action_required = 'Standard follow-up within 48 hours'
            escalate = False
        
        response = {
            'success': True,
            'urgency_score': urgency_score,
            'urgency_level': urgency_level,
            'action_required': action_required,
            'escalate': escalate,
            'keywords_detected': extract_urgency_keywords(lead_data.get('situation', ''))
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error analyzing urgency: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Urgency analysis temporarily unavailable'
        }), 500

@app.route('/api/ai/dashboard-stats', methods=['GET'])
def dashboard_stats():
    """
    Real-time dashboard statistics
    """
    try:
        # In production, this would pull from database
        # For demo, return sample statistics
        stats = {
            'success': True,
            'today': {
                'total_leads': 23,
                'p1_leads': 3,
                'p2_leads': 7,
                'p3_leads': 10,
                'p4_leads': 3,
                'avg_score': 142,
                'conversion_rate': 18.5
            },
            'week': {
                'total_leads': 156,
                'avg_score': 138,
                'conversion_rate': 22.1,
                'response_time_avg': '2.3 hours'
            },
            'top_counties': [
                {'name': 'Los Angeles', 'leads': 45, 'avg_score': 155},
                {'name': 'Orange', 'leads': 28, 'avg_score': 148},
                {'name': 'San Diego', 'leads': 22, 'avg_score': 142}
            ],
            'urgency_distribution': {
                'emergency': 8,
                'urgent': 24,
                'time_sensitive': 67,
                'standard': 57
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Dashboard temporarily unavailable'
        }), 500

@app.route('/api/ai/property-analysis', methods=['POST'])
def property_analysis():
    """
    AI-powered property value and foreclosure risk analysis
    """
    try:
        data = request.json
        address = data.get('property_address', '')
        loan_amount = data.get('loan_amount', 0)
        income = data.get('income', 0)
        
        # Analyze property using AI
        property_analyzer = lead_ai.property_analyzer
        estimated_value = property_analyzer.estimate_property_value(address)
        risk_score = property_analyzer.analyze_foreclosure_risk(
            estimated_value, loan_amount, income
        )
        
        # Generate analysis
        analysis = {
            'success': True,
            'estimated_value': estimated_value,
            'risk_score': risk_score,
            'risk_level': get_risk_level(risk_score),
            'loan_to_value': (loan_amount / estimated_value * 100) if estimated_value > 0 else 0,
            'recommendations': get_property_recommendations(risk_score, estimated_value, loan_amount),
            'market_insights': get_market_insights(address)
        }
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing property: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Property analysis temporarily unavailable'
        }), 500

@app.route('/api/ai/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring
    """
    return jsonify({
        'status': 'healthy',
        'ai_systems': {
            'lead_scoring': 'operational',
            'email_automation': 'operational',
            'property_analysis': 'operational'
        },
        'timestamp': datetime.now().isoformat()
    })

# Helper functions
def get_approach_strategy(score, lead_data):
    """Generate approach strategy based on score and lead characteristics"""
    if score >= 250:
        return "Emergency response protocol - immediate personal attention required"
    elif score >= 150:
        return "High-priority outreach with consultation scheduling"
    elif score >= 100:
        return "Professional follow-up with educational resources"
    else:
        return "Nurture sequence with value-based content"

def extract_urgency_keywords(situation):
    """Extract urgency keywords from situation description"""
    urgency_keywords = [
        'auction', 'sale date', 'notice of sale', 'trustee sale',
        'notice of default', 'nod', 'missed payments', 'behind on payments',
        'foreclosure notice', 'can\'t pay', 'lost job', 'bankruptcy'
    ]
    
    found_keywords = []
    situation_lower = situation.lower()
    
    for keyword in urgency_keywords:
        if keyword in situation_lower:
            found_keywords.append(keyword)
    
    return found_keywords

def get_risk_level(risk_score):
    """Convert risk score to risk level"""
    if risk_score >= 80:
        return 'Very High'
    elif risk_score >= 60:
        return 'High'
    elif risk_score >= 40:
        return 'Moderate'
    elif risk_score >= 20:
        return 'Low'
    else:
        return 'Very Low'

def get_property_recommendations(risk_score, value, loan_amount):
    """Generate property-specific recommendations"""
    recommendations = []
    
    if risk_score >= 80:
        recommendations.extend([
            "Immediate loan modification consultation recommended",
            "Explore emergency foreclosure prevention programs",
            "Consider short sale if property value below loan amount"
        ])
    elif risk_score >= 60:
        recommendations.extend([
            "Loan modification likely beneficial",
            "Review payment assistance programs",
            "Evaluate refinancing options"
        ])
    else:
        recommendations.extend([
            "Monitor payment schedule closely",
            "Build emergency fund for payments",
            "Consider refinancing for better terms"
        ])
    
    return recommendations

def get_market_insights(address):
    """Generate market insights for the area"""
    # In production, integrate with real estate APIs
    insights = {
        'market_trend': 'stable',
        'avg_time_on_market': '25 days',
        'foreclosure_rate': '2.3%',
        'market_conditions': 'Favorable for sellers'
    }
    
    return insights

if __name__ == '__main__':
    # Configure for production or development
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', 5000))
    
    logger.info(f"Starting AI API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)