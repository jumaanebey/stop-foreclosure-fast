# Virtual Consultation Conversion Tracking Setup

## Google Analytics 4 Events for Virtual Consultations

### Custom Events to Track

#### 1. Virtual Consultation Page Views
```javascript
// Track virtual consultation page visits
gtag('event', 'page_view', {
  'event_category': 'virtual_consultation',
  'event_label': 'landing_page_view',
  'page_title': 'Virtual Consultation California',
  'page_location': window.location.href
});
```

#### 2. Virtual Consultation Form Interactions
```javascript
// Track form field focus (engagement)
gtag('event', 'form_start', {
  'event_category': 'virtual_consultation',
  'event_label': 'form_engagement',
  'form_id': 'virtual-consultation-form'
});

// Track form submission
gtag('event', 'generate_lead', {
  'event_category': 'virtual_consultation',
  'event_label': 'form_submitted',
  'value': 1,
  'currency': 'USD',
  'urgency_level': '[urgency_value]',
  'county': '[county_value]'
});
```

#### 3. Phone Click Tracking
```javascript
// Track phone number clicks from virtual consultation pages
gtag('event', 'phone_call', {
  'event_category': 'virtual_consultation',
  'event_label': 'phone_click',
  'source_page': 'virtual_consultation'
});
```

#### 4. Consultation Booking Completion
```javascript
// Track successful consultation booking
gtag('event', 'purchase', {
  'event_category': 'virtual_consultation',
  'event_label': 'consultation_booked',
  'transaction_id': '[booking_id]',
  'value': 0, // Free consultation
  'currency': 'USD',
  'items': [{
    'item_id': 'virtual_consultation',
    'item_name': 'Virtual Foreclosure Consultation',
    'category': 'consultation',
    'quantity': 1,
    'price': 0
  }]
});
```

### Conversion Goals Setup

#### Primary Conversions:
1. **Virtual Consultation Form Submission** - Primary goal
2. **Phone Call from Virtual Pages** - Secondary goal
3. **Email Consultation Request** - Tertiary goal

#### Micro-Conversions:
1. **Virtual Consultation Page Time > 2 minutes**
2. **FAQ Section Engagement**
3. **Technology Requirements Page Views**
4. **Device Preference Selection**

## Enhanced Form Tracking

### Updated Virtual Consultation Form Script:
```javascript
document.addEventListener('DOMContentLoaded', function() {
    const consultationForm = document.getElementById('virtual-consultation-form');
    
    if (consultationForm) {
        // Track form start
        consultationForm.addEventListener('focusin', function(e) {
            if (!window.formStartTracked) {
                gtag('event', 'form_start', {
                    'event_category': 'virtual_consultation',
                    'event_label': 'form_engagement'
                });
                window.formStartTracked = true;
            }
        });
        
        // Track urgency selection
        const urgencySelect = document.getElementById('vc-urgency');
        if (urgencySelect) {
            urgencySelect.addEventListener('change', function() {
                gtag('event', 'urgency_selected', {
                    'event_category': 'virtual_consultation',
                    'event_label': this.value,
                    'urgency_level': this.value
                });
            });
        }
        
        // Track county selection
        const countySelect = document.getElementById('vc-county');
        if (countySelect) {
            countySelect.addEventListener('change', function() {
                gtag('event', 'county_selected', {
                    'event_category': 'virtual_consultation',
                    'event_label': this.value,
                    'county': this.value
                });
            });
        }
        
        // Track device preference
        const deviceSelect = document.getElementById('vc-device');
        if (deviceSelect) {
            deviceSelect.addEventListener('change', function() {
                gtag('event', 'device_preference', {
                    'event_category': 'virtual_consultation',
                    'event_label': this.value,
                    'device_type': this.value
                });
            });
        }
        
        // Form submission tracking
        consultationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // Enhanced tracking data
            data.type = 'virtual_consultation';
            data.timestamp = new Date().toISOString();
            data.source_page = window.location.pathname;
            data.referrer = document.referrer;
            data.user_agent = navigator.userAgent;
            
            // Track the lead generation event
            gtag('event', 'generate_lead', {
                'event_category': 'virtual_consultation',
                'event_label': 'form_submitted',
                'value': 1,
                'currency': 'USD',
                'urgency_level': data.urgency || 'not_specified',
                'county': data.county || 'not_specified',
                'device_preference': data.device_preference || 'not_specified'
            });
            
            // Submit to Google Sheets
            fetch('https://script.google.com/macros/s/AKfycbwot6SWKdQKzoOmVizO8_mh93aU_A6cIkGnpu5yrnzmPrfkn4pDQ7E07asi1_PXSpsq/exec', {
                method: 'POST',
                mode: 'no-cors',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(() => {
                // Track successful submission
                gtag('event', 'form_submit_success', {
                    'event_category': 'virtual_consultation',
                    'event_label': 'google_sheets_success'
                });
                
                alert('Thank you! We will contact you within 2 hours to schedule your virtual consultation.');
                
                // Optional: redirect to thank you page
                // window.location.href = 'thank-you-virtual-consultation.html';
            })
            .catch(error => {
                gtag('event', 'form_submit_error', {
                    'event_category': 'virtual_consultation',
                    'event_label': 'submission_failed'
                });
                
                console.error('Form submission error:', error);
                alert('There was an error submitting your form. Please call us at (949) 328-4811 to schedule your consultation.');
            });
        });
    }
});
```

## Lead Scoring and Segmentation

### Urgency-Based Lead Scoring:
```javascript
const urgencyScoring = {
    'immediate': 100,     // Auction within 30 days
    'urgent': 80,        // Notice of sale received
    'soon': 60,          // Notice of default
    'exploring': 40,     // Behind on payments
    'planning': 20       // Want to understand options
};

// Add to form submission
data.lead_score = urgencyScoring[data.urgency] || 0;
```

### Geographic Lead Segmentation:
```javascript
const countyTiers = {
    'Los Angeles': 'tier1_metro',
    'Orange': 'tier1_metro', 
    'San Diego': 'tier1_metro',
    'Riverside': 'tier2_suburban',
    'San Bernardino': 'tier2_suburban',
    'Ventura': 'tier2_suburban',
    'Fresno': 'tier3_rural',
    'Imperial': 'tier3_rural',
    'Mono': 'tier3_rural'
};

// Add to tracking
data.county_tier = countyTiers[data.county] || 'tier3_rural';
```

## Facebook Pixel Integration

### Virtual Consultation Events:
```javascript
// Page view tracking
fbq('track', 'PageView');

// Lead generation tracking
fbq('track', 'Lead', {
    content_name: 'Virtual Foreclosure Consultation',
    content_category: 'Real Estate Service',
    value: 0,
    currency: 'USD'
});

// Form completion tracking
fbq('track', 'CompleteRegistration', {
    content_name: 'Virtual Consultation Booking',
    status: 'completed'
});
```

## Call Tracking Implementation

### Dynamic Number Insertion:
```javascript
// Track phone clicks with source attribution
document.addEventListener('DOMContentLoaded', function() {
    const phoneLinks = document.querySelectorAll('a[href^="tel:"]');
    
    phoneLinks.forEach(link => {
        link.addEventListener('click', function() {
            gtag('event', 'phone_call', {
                'event_category': 'virtual_consultation',
                'event_label': 'phone_click',
                'source_page': window.location.pathname,
                'link_text': this.textContent.trim()
            });
            
            // Facebook Pixel call tracking
            fbq('track', 'Contact', {
                content_name: 'Virtual Consultation Phone Call'
            });
        });
    });
});
```

## Conversion Funnel Analysis

### Virtual Consultation Funnel Stages:
1. **Awareness:** Virtual consultation page visit
2. **Interest:** Form field interaction or FAQ reading
3. **Consideration:** Device preference selection or urgency indication
4. **Intent:** Form completion or phone call
5. **Action:** Successful consultation booking

### Funnel Tracking Events:
```javascript
// Stage 1: Awareness
gtag('event', 'funnel_stage_1', {
    'event_category': 'virtual_consultation_funnel',
    'event_label': 'awareness',
    'funnel_stage': 'page_view'
});

// Stage 2: Interest  
gtag('event', 'funnel_stage_2', {
    'event_category': 'virtual_consultation_funnel',
    'event_label': 'interest',
    'funnel_stage': 'form_interaction'
});

// Stage 3: Consideration
gtag('event', 'funnel_stage_3', {
    'event_category': 'virtual_consultation_funnel',
    'event_label': 'consideration',
    'funnel_stage': 'preferences_selected'
});

// Stage 4: Intent
gtag('event', 'funnel_stage_4', {
    'event_category': 'virtual_consultation_funnel',
    'event_label': 'intent',
    'funnel_stage': 'form_submitted'
});

// Stage 5: Action
gtag('event', 'funnel_stage_5', {
    'event_category': 'virtual_consultation_funnel',
    'event_label': 'action',
    'funnel_stage': 'consultation_completed'
});
```

## ROI Calculation Framework

### Virtual Consultation Value Metrics:
- **Cost per Virtual Lead:** Marketing spend ÷ virtual consultation requests
- **Virtual Consultation Conversion Rate:** Consultations completed ÷ form submissions
- **Cash Offer Conversion Rate:** Cash offers accepted ÷ consultations completed
- **Average Deal Value:** Total transaction value ÷ number of deals
- **Lifetime Customer Value:** Repeat business + referrals value

### Monthly Reporting Dashboard:
1. **Virtual consultation page traffic:** Sessions, unique visitors, time on page
2. **Form conversion rates:** Submissions ÷ page visits
3. **Lead quality scoring:** Urgency level distribution
4. **Geographic performance:** Conversion rates by county
5. **Device preference trends:** Technology adoption patterns
6. **Follow-through rates:** Consultations completed ÷ forms submitted

## Implementation Checklist:

### Week 1: Basic Tracking
- ✅ Google Analytics 4 event tracking setup
- ✅ Form interaction monitoring
- ✅ Phone click tracking
- ✅ Basic conversion goals

### Week 2: Enhanced Analytics
- ✅ Lead scoring implementation
- ✅ Geographic segmentation
- ✅ Urgency-based tracking
- ✅ Device preference monitoring

### Week 3: Advanced Tracking
- ✅ Facebook Pixel integration
- ✅ Funnel stage tracking
- ✅ Call tracking enhancement
- ✅ ROI calculation setup

### Week 4: Optimization
- ✅ Performance analysis
- ✅ Conversion rate optimization
- ✅ A/B testing setup
- ✅ Reporting dashboard creation

This comprehensive tracking system provides detailed insights into virtual consultation performance, allowing for data-driven optimization of your online foreclosure business.