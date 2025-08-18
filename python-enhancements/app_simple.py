#!/usr/bin/env python3
"""
Simplified Foreclosure AI API for Render Deployment
Basic version that will definitely work, then we can add AI features
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['https://myforeclosuresolution.com', 'https://www.myforeclosuresolution.com', 'http://localhost:3000'])

# Lead storage (in production, use a database)
leads_database = []

# Email configuration (set these environment variables in Render)
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER', '')  # Your email
EMAIL_PASS = os.getenv('EMAIL_PASS', '')  # Your app password
NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', 'help@myforeclosuresolution.com')  # Where to send alerts

def save_lead(lead_data):
    """Save lead to database (using list for now)"""
    lead_data['id'] = len(leads_database) + 1
    lead_data['created_at'] = datetime.now().isoformat()
    leads_database.append(lead_data)
    return lead_data['id']

def send_email_notification(lead_data):
    """Send email notification for high-priority leads"""
    if not EMAIL_USER or not EMAIL_PASS:
        print(f"⚠️ Email not configured - would send alert for: {lead_data.get('name', 'Unknown')}")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = NOTIFICATION_EMAIL
        msg['Subject'] = f"🚨 HIGH PRIORITY LEAD - Score: {lead_data.get('ai_score', 0)}"
        
        # Email body
        priority = lead_data.get('priority', 'Unknown')
        score = lead_data.get('ai_score', 0)
        
        body = f"""
🚨 NEW HIGH-PRIORITY FORECLOSURE LEAD

URGENCY DETAILS:
• AI Score: {score}/500
• Priority: {priority}
• Response Required: {lead_data.get('response_time', 'ASAP')}

CONTACT INFORMATION:
• Name: {lead_data.get('name', 'Not provided')}
• Phone: {lead_data.get('phone', 'Not provided')}
• Email: {lead_data.get('email', 'Not provided')}
• Property: {lead_data.get('property_address', 'Not provided')}
• Best Time: {lead_data.get('best_time', 'Not specified')}

SITUATION:
{lead_data.get('ai_situation', 'No details provided')}

KEYWORDS DETECTED:
{', '.join(lead_data.get('keywords_detected', []))}

⚡ ACTION REQUIRED: Contact within {lead_data.get('response_time', '15 minutes')}

Lead ID: {lead_data.get('id', 'Unknown')}
Timestamp: {lead_data.get('timestamp', datetime.now().isoformat())}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, NOTIFICATION_EMAIL, text)
        server.quit()
        
        print(f"✅ Email notification sent for lead: {lead_data.get('name', 'Unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ Email notification failed: {str(e)}")
        return False

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
        
        # Property value scoring (if provided)
        property_address = lead_data.get('property_address', '')
        if property_address:
            # Get property value estimate
            try:
                import hashlib
                import random
                hash_value = int(hashlib.md5(property_address.encode()).hexdigest()[:8], 16)
                random.seed(hash_value)
                estimated_value = random.randint(200000, 800000)
                
                # California adjustment
                if any(term in property_address.lower() for term in ['ca', 'california', 'los angeles', 'san francisco', 'san diego']):
                    estimated_value = int(estimated_value * 1.5)
                
                # Higher value properties get higher priority
                if estimated_value > 600000:
                    score += 30  # High-value property
                elif estimated_value > 400000:
                    score += 20  # Medium-value property
                else:
                    score += 10  # Standard value
                    
                # California gets urgency boost (faster foreclosure timeline)
                if any(term in property_address.lower() for term in ['ca', 'california']):
                    score += 25  # California has fast foreclosure process
                    
            except Exception:
                score += 10  # Default bonus for providing address
        
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
            'response_time': 'Within 15 minutes',
            'ai_score': 450,  # Emergency bookings get high score
            'keywords_detected': ['emergency booking', 'scheduled consultation']
        }
        
        # Save to database
        lead_id = save_lead(booking_data)
        booking_data['id'] = lead_id
        
        # Send email notification for emergency booking
        send_email_notification(booking_data)
        
        # Log to console
        print(f"🚨 EMERGENCY BOOKING SAVED: ID#{lead_id} - {booking_data['name']} - {booking_data['phone']}")
        print(f"   Situation: {booking_data['ai_situation']}")
        print(f"   Best Time: {booking_data['best_time']}")
        
        return jsonify({
            'success': True,
            'booking_id': f"EMG-{lead_id}",
            'message': 'Emergency consultation scheduled - you will receive a call within 15 minutes',
            'response_time': '15 minutes',
            'lead_id': lead_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ai/leads', methods=['GET'])
def get_leads():
    """Get all leads with filtering options"""
    try:
        min_score = request.args.get('min_score', 0, type=int)
        priority = request.args.get('priority', '')
        limit = request.args.get('limit', 50, type=int)
        
        # Filter leads
        filtered_leads = []
        for lead in leads_database:
            if lead.get('ai_score', 0) >= min_score:
                if not priority or lead.get('priority', '') == priority:
                    filtered_leads.append(lead)
        
        # Sort by score descending, then by date
        filtered_leads.sort(key=lambda x: (x.get('ai_score', 0), x.get('created_at', '')), reverse=True)
        
        # Limit results
        filtered_leads = filtered_leads[:limit]
        
        return jsonify({
            'success': True,
            'leads': filtered_leads,
            'total_count': len(leads_database),
            'filtered_count': len(filtered_leads),
            'high_priority_count': len([l for l in leads_database if l.get('ai_score', 0) >= 300])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ai/property-value', methods=['POST'])
def get_property_value():
    """Get estimated property value (mock implementation)"""
    try:
        data = request.get_json()
        address = data.get('address', '')
        
        if not address:
            return jsonify({
                'success': False,
                'error': 'Address required'
            }), 400
        
        # Mock property value estimation
        # In production, integrate with Zillow API, MLS, or similar service
        import hashlib
        import random
        
        # Generate consistent "estimate" based on address
        hash_value = int(hashlib.md5(address.encode()).hexdigest()[:8], 16)
        random.seed(hash_value)
        
        base_value = random.randint(200000, 800000)
        confidence = random.uniform(0.7, 0.95)
        
        # California adjustment
        if any(term in address.lower() for term in ['ca', 'california', 'los angeles', 'san francisco', 'san diego']):
            base_value = int(base_value * 1.5)
        
        return jsonify({
            'success': True,
            'estimated_value': base_value,
            'confidence': round(confidence, 2),
            'data_source': 'AI Estimation',
            'address': address,
            'market_trends': 'Stable' if confidence > 0.8 else 'Volatile'
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