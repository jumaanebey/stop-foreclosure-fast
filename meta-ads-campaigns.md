# Meta Lead Ads Campaign Structure

## Account Setup Requirements:
- **Special Ad Category:** Housing
- **Compliance:** Fair Housing Act requirements
- **Business Verification:** Completed for housing ads
- **Payment Method:** Set up with sufficient credit limit

---

## Campaign 1: Foreclosure Help - Cold Audience
**Objective:** Lead Generation
**Budget:** $75/day
**Placement:** Advantage+ Placements
**Special Category:** Housing

### Ad Sets:
1. **Interest + Behavioral Targeting**
   - **Interests:** Real estate, homeownership, financial planning
   - **Behaviors:** Likely to move, mortgage refinancing
   - **Demographics:** Ages 35-65, homeowners
   - **Location:** California statewide
   
2. **Life Events Targeting**
   - **Life Events:** Recently moved, new job, financial hardship
   - **Income:** Top 25-50% (avoid fair housing violations)
   - **Location:** Major CA metro areas

### Creative Variations:
**Video Ads (Primary):**
- **Hook 1:** "Facing foreclosure in California? You have options."
- **Hook 2:** "Got a foreclosure notice? Don't panic. Get help."
- **Hook 3:** "Stop foreclosure in 24 hours. Licensed CA professional."

**Static Image Ads:**
- Professional headshot with "Licensed CA Real Estate Professional"
- Home exterior with "Keep Your Home or Sell Fast"
- Document imagery with "Multiple Options Available"

### Lead Form:
**Form Name:** "Get Foreclosure Options - California"
**Questions:**
1. Property Address (required)
2. Current Situation (multiple choice):
   - Received notice of default
   - Behind on payments
   - Sale scheduled
   - Exploring options
3. Preferred Outcome (multiple choice):
   - Keep my home
   - Sell quickly
   - Claim surplus funds
   - Not sure
4. Name (required)
5. Phone (required)
6. Email (required)

**TCPA Disclaimer:** "By submitting, I agree to be contacted by phone, text, and email regarding foreclosure assistance services."

---

## Campaign 2: Lookalike Audiences
**Objective:** Lead Generation  
**Budget:** $50/day
**Optimization:** Lead Quality (use value-based lookalikes)

### Ad Sets:
1. **1% Lookalike - Website Converters**
   - Source: Pixel events from form completions
   - Location: California
   - Age: 30-65
   
2. **1% Lookalike - Phone Call Converters** 
   - Source: CallRail phone tracking data
   - Quality score: Calls >2 minutes
   
3. **Flex Lookalike (1-10%)**
   - Let Meta find best performing percentage
   - Higher budget allocation for testing

---

## Campaign 3: Retargeting - Warm Audience
**Objective:** Lead Generation
**Budget:** $25/day
**Frequency Cap:** 3 impressions per 7 days

### Ad Sets:
1. **Website Visitors - No Lead**
   - Visited in last 30 days
   - Did not complete lead form
   - More urgent messaging

2. **Video Viewers - 25%+**
   - Watched video ads 25% or more
   - Different angle: surplus funds focus
   
3. **Lead Form Starters**
   - Started but didn't complete form
   - Simplified form + phone CTA

### Retargeting Creative:
**Urgent Messaging:**
- "Still dealing with foreclosure? Get help now."
- "Don't wait - foreclosure timelines are strict."
- "Ready to explore your options? Start here."

---

## Creative Guidelines:

### Fair Housing Compliance:
- ✅ "Available to all qualified homeowners"
- ✅ Focus on service benefits, not demographics  
- ✅ "Licensed CA real estate professional"
- ❌ No family imagery unless diverse
- ❌ No demographic-specific targeting language
- ❌ No discriminatory language

### High-Performing Creative Elements:
1. **Professional Credibility:**
   - License numbers visible
   - Professional headshots
   - Office/business imagery

2. **Urgency Indicators:**
   - "24-hour response"
   - "Time-sensitive situation"
   - "Act before it's too late"

3. **Option Clarity:**
   - "Multiple paths available"
   - "Keep home, sell fast, or surplus recovery"
   - "No obligation consultation"

4. **Local Relevance:**
   - "California homeowners"
   - "CA foreclosure laws"
   - "Serving all 58 counties"

---

## Audience Exclusions:
- Previous customers
- Age <25 (rare homeowners)
- Renters (behavior-based)
- Recent movers (if targeting distressed homeowners)

---

## Budget Allocation Strategy:
**Month 1:** $150/day total
- Cold: $75/day (50%)
- Lookalike: $50/day (33%) 
- Retargeting: $25/day (17%)

**Month 2+:** Based on CPL performance
- Increase budget on best-performing ad sets
- Pause underperforming audiences
- Test new lookalike percentages

---

## Performance Benchmarks:

### CPL Targets:
- **Cold Audiences:** $30-120
- **Lookalike:** $25-90
- **Retargeting:** $15-60

### Lead Quality Indicators:
- **Phone Answer Rate:** >40%
- **Appointment Show Rate:** >60%
- **Qualification Rate:** >25%

### Optimization Events:
1. **Lead (Standard Event)**
2. **Schedule (Custom Event)**
3. **Qualified Lead (Custom Conversion)**
4. **Phone Call >60s (Offline Conversion)**

---

## A/B Testing Schedule:

### Week 1-2:
- Test 3 different hooks
- Test video vs. static image
- Test form length (4 vs. 6 questions)

### Week 3-4:
- Test different audience sizes
- Test broad vs. detailed targeting
- Test urgency vs. educational angles

### Month 2:
- Test lookalike percentages (1% vs 2-5% vs 6-10%)
- Test placement optimization
- Test bid strategies

---

## Conversion API Setup:
**Server-Side Events:** Essential for iOS 14.5+ privacy
- Lead form completions
- Phone number clicks
- Appointment bookings
- Qualified lead classifications

**Implementation:**
- Facebook Conversions API
- Google Tag Manager Server Container
- CallRail offline conversions integration

---

## Creative Production Schedule:
**Monthly Refresh:**
- 2 new video ads
- 4 new static images  
- 2 new carousel ads
- 1 collection ad

**Seasonal Updates:**
- Holiday impact messaging
- Economic condition awareness
- California housing market updates

---

## Compliance Monitoring:
- **Weekly:** Ad performance and approval status
- **Monthly:** Fair housing compliance review
- **Quarterly:** Creative compliance audit
- **Semi-Annual:** Account policy review

---

## Integration with Google Ads:
- **Shared Audiences:** Import Google audiences to Facebook
- **Creative Testing:** Cross-platform creative performance
- **Keyword Insights:** Use Google search terms for Facebook interests
- **Attribution:** First-touch vs. last-touch analysis