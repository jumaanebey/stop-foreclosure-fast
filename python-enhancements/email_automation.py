#!/usr/bin/env python3
"""
Advanced Email Automation for Virtual Foreclosure Business
AI-powered personalization and timing optimization
"""

import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import pandas as pd
from datetime import datetime, timedelta
import schedule
import time
import openai
from jinja2 import Template
import requests

class EmailPersonalizationAI:
    """
    AI-powered email content personalization
    """
    
    def __init__(self, openai_api_key=None):
        if openai_api_key:
            openai.api_key = openai_api_key
    
    def generate_personalized_content(self, lead_data, email_type='welcome'):
        """
        Generate personalized email content using AI
        """
        urgency = lead_data.get('urgency_level', 'standard')
        county = lead_data.get('county', 'California')
        name = lead_data.get('name', 'there')
        situation = lead_data.get('situation', '')
        
        prompts = {
            'welcome': f"""
            Write a personalized welcome email for a homeowner in {county} facing foreclosure.
            Urgency level: {urgency}
            Situation: {situation}
            Name: {name}
            
            Make it empathetic, professional, and action-oriented. Include:
            - Acknowledgment of their specific situation
            - Confidence and hope
            - Clear next steps
            - Professional credentials (DRE #02076038 | NMLS #2033637)
            - Virtual consultation benefits
            
            Keep it under 300 words.
            """,
            
            'follow_up': f"""
            Write a follow-up email for {name} in {county} who hasn't responded to initial contact.
            Urgency: {urgency}
            
            Include:
            - Gentle reminder about their foreclosure situation
            - New resources or insights
            - Alternative contact methods
            - Urgency without pressure
            - Success story from similar situation
            
            Keep it under 200 words.
            """,
            
            'emergency': f"""
            Write an emergency response email for {name} in {county}.
            Situation: {situation}
            
            This is time-critical. Include:
            - Immediate action items
            - Emergency contact information
            - Same-day consultation availability
            - Reassurance and expertise
            - Clear timeline expectations
            
            Keep it under 250 words, urgent but professional tone.
            """
        }
        
        # If OpenAI available, use it. Otherwise, use templates
        try:
            if openai.api_key:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompts.get(email_type, prompts['welcome']),
                    max_tokens=400,
                    temperature=0.7
                )
                return response.choices[0].text.strip()
        except:
            pass
        
        # Fallback to template-based personalization
        return self.template_based_personalization(lead_data, email_type)
    
    def template_based_personalization(self, lead_data, email_type):
        """
        Template-based personalization when AI not available
        """
        templates = {
            'welcome': """
            Hi {{ name }},
            
            Thank you for reaching out about foreclosure help in {{ county }}. I understand this is a stressful time, and I want you to know that you're not alone.
            
            {% if urgency == 'emergency' %}
            Given the urgent nature of your situation, I've prioritized your case for immediate review. Our team can provide same-day virtual consultation to explore your options.
            {% elif urgency == 'urgent' %}
            Your situation requires prompt attention, and I'm here to help. We can schedule a virtual consultation within 24 hours to discuss your options.
            {% else %}
            Every foreclosure situation is unique, and there are often more solutions available than homeowners realize.
            {% endif %}
            
            As a licensed California real estate professional (DRE #02076038 | NMLS #2033637), I've helped hundreds of {{ county }} homeowners avoid foreclosure since 2014. Virtual consultations allow us to work together regardless of your location, often leading to faster solutions.
            
            Your next step: Book a free virtual consultation at your convenience. We'll review your situation and create a personalized action plan.
            
            Stay strong,
            My Foreclosure Solution Team
            (949) 328-4811
            """,
            
            'follow_up': """
            Hi {{ name }},
            
            I wanted to follow up on your foreclosure situation in {{ county }}. Sometimes homeowners feel overwhelmed and aren't sure where to start - that's completely normal.
            
            {% if urgency == 'emergency' %}
            Time is critical in your situation. Even if you're unsure about next steps, a quick virtual consultation can clarify your options and timeline.
            {% else %}
            I wanted to share a recent success story: Last week, we helped a {{ county }} family avoid foreclosure through a virtual consultation that took just 45 minutes. They're now on a payment plan that saves their home.
            {% endif %}
            
            Sometimes a simple conversation can reveal solutions you didn't know existed. Our virtual consultations are:
            ✓ Completely free and no-obligation
            ✓ Available evenings and weekends
            ✓ Private and confidential
            
            Ready to explore your options? Reply to this email or call (949) 328-4811.
            
            Here to help,
            My Foreclosure Solution Team
            """
        }
        
        template = Template(templates.get(email_type, templates['welcome']))
        return template.render(
            name=lead_data.get('name', 'there'),
            county=lead_data.get('county', 'California'),
            urgency=lead_data.get('urgency_level', 'standard')
        )

class SmartEmailScheduler:
    """
    Intelligent email scheduling based on recipient behavior and optimal timing
    """
    
    def __init__(self, smtp_server, smtp_port, email_user, email_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_user = email_user
        self.email_password = email_password
        self.email_queue = []
        
    def add_to_queue(self, lead_data, email_type, send_time=None):
        """
        Add email to smart scheduling queue
        """
        if not send_time:
            send_time = self.calculate_optimal_send_time(lead_data)
        
        email_item = {
            'lead_data': lead_data,
            'email_type': email_type,
            'send_time': send_time,
            'created_at': datetime.now(),
            'attempts': 0,
            'max_attempts': 3
        }
        
        self.email_queue.append(email_item)
        return email_item
    
    def calculate_optimal_send_time(self, lead_data):
        """
        Calculate optimal send time based on lead characteristics
        """
        now = datetime.now()
        
        # Emergency leads - send immediately
        if lead_data.get('urgency_level') == 'emergency':
            return now + timedelta(minutes=5)
        
        # Consider time zone (California-based business)
        optimal_hour = 10  # Default 10 AM
        
        # Adjust based on lead source and device
        device_type = lead_data.get('device_type', 'desktop')
        lead_source = lead_data.get('lead_source', 'direct')
        
        if device_type == 'mobile':
            # Mobile users often check email during commute or breaks
            if now.hour < 8:
                optimal_hour = 8  # Morning commute
            elif now.hour < 12:
                optimal_hour = 12  # Lunch break
            elif now.hour < 17:
                optimal_hour = 17  # Evening commute
            else:
                optimal_hour = 19  # Evening
        
        if lead_source == 'google_my_business':
            # GMB users often research during business hours
            optimal_hour = 14  # 2 PM - afternoon research time
        
        # Schedule for next optimal time
        target_time = now.replace(hour=optimal_hour, minute=0, second=0, microsecond=0)
        
        # If optimal time has passed today, schedule for tomorrow
        if target_time <= now:
            target_time += timedelta(days=1)
        
        # Avoid weekends for business emails (unless emergency)
        while target_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
            target_time += timedelta(days=1)
        
        return target_time
    
    def send_email(self, email_item):
        """
        Send individual email with personalized content
        """
        try:
            lead_data = email_item['lead_data']
            email_type = email_item['email_type']
            
            # Generate personalized content
            personalizer = EmailPersonalizationAI()
            content = personalizer.generate_personalized_content(lead_data, email_type)
            
            # Create email
            msg = MimeMultipart()
            msg['From'] = self.email_user
            msg['To'] = lead_data['email']
            
            # Personalized subject lines
            subject_lines = {
                'welcome': f"Your {lead_data.get('county', 'California')} Foreclosure Resources Are Ready",
                'follow_up': f"Following Up on Your {lead_data.get('county', 'California')} Foreclosure Situation",
                'emergency': f"🚨 URGENT: {lead_data.get('county', 'California')} Foreclosure Emergency Response"
            }
            
            msg['Subject'] = subject_lines.get(email_type, subject_lines['welcome'])
            
            # Add personalized content
            msg.attach(MimeText(content, 'plain'))
            
            # Add HTML version with better formatting
            html_content = self.convert_to_html(content, lead_data)
            msg.attach(MimeText(html_content, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_user, lead_data['email'], text)
            server.quit()
            
            # Log successful send
            print(f"Email sent successfully to {lead_data['email']} at {datetime.now()}")
            return True
            
        except Exception as e:
            print(f"Error sending email to {lead_data['email']}: {str(e)}")
            email_item['attempts'] += 1
            return False
    
    def convert_to_html(self, plain_content, lead_data):
        """
        Convert plain text to professional HTML email
        """
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">My Foreclosure Solution</h1>
                <p style="margin: 10px 0 0 0;">California's Virtual Foreclosure Specialists</p>
            </div>
            
            <div style="background: #ffffff; padding: 30px; border: 1px solid #e5e5e5; border-top: none;">
                {{ content }}
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e5e5;">
                    <p style="margin: 0;"><strong>Licensed California Real Estate Professional</strong><br>
                    DRE #02076038 | NMLS #2033637<br>
                    📞 (949) 328-4811<br>
                    📧 help@myforeclosuresolution.com</p>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #6b7280;">
                <p>You received this email because you requested foreclosure help in California.</p>
            </div>
        </body>
        </html>
        """
        
        # Convert plain text to HTML paragraphs
        html_content = plain_content.replace('\n\n', '</p><p>').replace('\n', '<br>')
        html_content = f"<p>{html_content}</p>"
        
        template = Template(html_template)
        return template.render(content=html_content)
    
    def process_queue(self):
        """
        Process the email queue - send emails that are ready
        """
        now = datetime.now()
        emails_to_send = [email for email in self.email_queue if email['send_time'] <= now]
        
        for email_item in emails_to_send:
            if email_item['attempts'] < email_item['max_attempts']:
                success = self.send_email(email_item)
                if success:
                    self.email_queue.remove(email_item)
                # If failed, will retry next time (attempts incremented in send_email)
            else:
                # Max attempts reached, remove from queue
                print(f"Max attempts reached for {email_item['lead_data']['email']}")
                self.email_queue.remove(email_item)
    
    def start_scheduler(self):
        """
        Start the email scheduler to run continuously
        """
        schedule.every(5).minutes.do(self.process_queue)
        
        print("Email scheduler started. Processing queue every 5 minutes...")
        while True:
            schedule.run_pending()
            time.sleep(60)

class EmailCampaignAnalyzer:
    """
    Analyze email campaign performance and optimize
    """
    
    def __init__(self):
        self.campaign_data = []
    
    def track_email_performance(self, email_data, open_rate=None, click_rate=None, response_rate=None):
        """
        Track email performance metrics
        """
        performance = {
            'email_id': email_data.get('id'),
            'send_time': email_data.get('send_time'),
            'recipient': email_data.get('recipient'),
            'email_type': email_data.get('email_type'),
            'subject_line': email_data.get('subject'),
            'open_rate': open_rate,
            'click_rate': click_rate,
            'response_rate': response_rate,
            'timestamp': datetime.now()
        }
        
        self.campaign_data.append(performance)
    
    def analyze_optimal_timing(self):
        """
        Analyze optimal send times based on performance data
        """
        if not self.campaign_data:
            return "Insufficient data for analysis"
        
        df = pd.DataFrame(self.campaign_data)
        df['hour'] = pd.to_datetime(df['send_time']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['send_time']).dt.dayofweek
        
        # Find best performing hours
        hourly_performance = df.groupby('hour')['open_rate'].mean().sort_values(ascending=False)
        best_hours = hourly_performance.head(3).index.tolist()
        
        # Find best performing days
        daily_performance = df.groupby('day_of_week')['open_rate'].mean().sort_values(ascending=False)
        best_days = daily_performance.head(3).index.tolist()
        
        return {
            'best_hours': best_hours,
            'best_days': best_days,
            'overall_open_rate': df['open_rate'].mean(),
            'overall_click_rate': df['click_rate'].mean()
        }

# Example usage and integration
if __name__ == "__main__":
    # Initialize email scheduler
    scheduler = SmartEmailScheduler(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        email_user="help@myforeclosuresolution.com",
        email_password="your-app-password"
    )
    
    # Example lead data
    sample_lead = {
        'name': 'Sarah Johnson',
        'email': 'sarah@example.com',
        'phone': '555-0123',
        'county': 'Orange County',
        'urgency_level': 'urgent',
        'device_type': 'mobile',
        'lead_source': 'google_organic',
        'situation': 'Received notice of default, need help fast'
    }
    
    # Add welcome email to queue with smart scheduling
    scheduler.add_to_queue(sample_lead, 'welcome')
    
    # Process emails (in production, this would run continuously)
    scheduler.process_queue()