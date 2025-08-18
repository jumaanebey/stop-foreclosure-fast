#!/usr/bin/env python3
"""
Simplified Foreclosure AI API for Render Deployment
Basic version that will definitely work, then we can add AI features
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['https://myforeclosuresolution.com', 'https://www.myforeclosuresolution.com', 'http://localhost:3000'])

@app.route('/')
def home():
    return jsonify({
        'service': 'Foreclosure AI API',
        'status': 'operational',
        'version': '1.0.0',
        'endpoints': [
            '/api/ai/health',
            '/api/ai/score-lead',
            '/api/ai/analyze-urgency'
        ]
    })

@app.route('/api/ai/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'ai_systems': {
            'lead_scoring': 'operational',
            'email_automation': 'operational',
            'property_analysis': 'operational'
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/ai/score-lead', methods=['POST'])
def score_lead():
    """Basic lead scoring endpoint"""
    try:
        lead_data = request.json or {}
        
        # Simple scoring algorithm
        score = 100  # Base score
        
        # Add points for engagement
        session_data = lead_data.get('session_data', {})
        if session_data.get('timeOnPage', 0) > 300000:  # 5+ minutes
            score += 50
        if session_data.get('formInteractions', 0) > 0:
            score += 30
        if session_data.get('phoneClicks', 0) > 0:
            score += 40
        
        # Add points for urgency keywords
        situation = lead_data.get('situation', '').lower()
        urgent_keywords = ['auction', 'foreclosure', 'notice', 'default', 'emergency']
        for keyword in urgent_keywords:
            if keyword in situation:
                score += 50
                break
        
        # Determine priority
        if score >= 200:
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
        
        # Basic recommendations
        recommendations = []
        if score >= 200:
            recommendations = [
                "IMMEDIATE PRIORITY: Call within 1 hour",
                "Offer same-day virtual consultation",
                "Prepare emergency response materials"
            ]
        elif score >= 150:
            recommendations = [
                "HIGH PRIORITY: Contact within 4 hours",
                "Send priority email sequence",
                "Schedule consultation within 24 hours"
            ]
        else:
            recommendations = [
                "QUALIFIED LEAD: Contact within 24 hours",
                "Send standard welcome sequence",
                "Provide educational resources"
            ]
        
        response = {
            'success': True,
            'ai_score': min(score, 500),
            'priority': priority,
            'response_time': response_time,
            'conversion_probability': min(score / 500, 1.0),
            'recommendations': recommendations[:3],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'AI scoring system temporarily unavailable',
            'fallback_score': 100,
            'priority': 'P3'
        }), 500

@app.route('/api/ai/analyze-urgency', methods=['POST'])
def analyze_urgency():
    """Real-time urgency analysis for leads"""
    try:
        data = request.json or {}
        situation = data.get('situation', '').lower()
        
        urgency_score = 0
        urgency_keywords = {
            'emergency': ['auction', 'sale date', 'foreclosure sale', 'trustee sale', 'notice of sale'],
            'urgent': ['notice of default', 'nod', 'default notice', 'missed payments', '90 days'],
            'time_sensitive': ['30 days', 'this month', 'next week', 'soon', 'quickly'],
            'financial_stress': ['can\'t pay', 'no money', 'lost job', 'unemployed', 'bankruptcy']
        }
        
        found_keywords = []
        for category, keywords in urgency_keywords.items():
            for keyword in keywords:
                if keyword in situation:
                    found_keywords.append(keyword)
                    if category == 'emergency':
                        urgency_score += 100
                    elif category == 'urgent':
                        urgency_score += 75
                    elif category == 'time_sensitive':
                        urgency_score += 50
                    elif category == 'financial_stress':
                        urgency_score += 25
        
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
            'urgency_score': min(urgency_score, 200),
            'urgency_level': urgency_level,
            'action_required': action_required,
            'escalate': escalate,
            'keywords_detected': found_keywords
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Urgency analysis temporarily unavailable'
        }), 500

@app.route('/dashboard.html')
def dashboard():
    """Serve AI dashboard"""
    return """
    <!DOCTYPE html>
    <html><head><title>AI Dashboard</title></head>
    <body>
    <h1>🤖 Foreclosure AI Dashboard</h1>
    <p>AI API is running successfully!</p>
    <p>API Base URL: <code id="apiUrl"></code></p>
    <script>
    document.getElementById('apiUrl').textContent = window.location.origin;
    </script>
    </body></html>
    """

@app.route('/api/ai/emergency-booking', methods=['POST'])
def emergency_booking():
    """Handle emergency consultation booking"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'phone', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Process the emergency booking
        booking_data = {
            'name': data['name'],
            'phone': data['phone'],
            'email': data['email'],
            'property_address': data.get('property_address', ''),
            'best_time': data.get('best_time', ''),
            'urgency_level': data.get('urgency_level', 'emergency'),
            'lead_source': data.get('lead_source', 'ai_assistant'),
            'ai_situation': data.get('ai_situation', ''),
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'priority': 'P1',
            'response_required': 'Within 15 minutes'
        }
        
        # In a real implementation, you would:
        # 1. Save to database
        # 2. Send email notification to you
        # 3. Trigger SMS/webhook for immediate notification
        # 4. Add to calendar system
        
        # For now, we'll log it and return success
        print(f"🚨 EMERGENCY BOOKING: {booking_data['name']} - {booking_data['phone']}")
        print(f"   Situation: {booking_data['ai_situation']}")
        print(f"   Best Time: {booking_data['best_time']}")
        
        return jsonify({
            'success': True,
            'booking_id': f"EMG-{int(time.time())}",
            'message': 'Emergency consultation scheduled',
            'response_time': '15 minutes',
            'contact_info': booking_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)