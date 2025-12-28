# 🚀 ConvertKit Setup Guide for Email Sequences

## **Step 1: Create the Email Sequences**

### 🔥 **Urgent Foreclosure Sequence**
1. Go to ConvertKit → Automations → Create New Sequence
2. Name: "Urgent Foreclosure - 5 Day Sequence"
3. Create 5 emails with these delays:
   - Email 1: Immediately (0 hours)
   - Email 2: 1 day delay
   - Email 3: 3 days delay  
   - Email 4: 5 days delay
   - Email 5: 7 days delay

### 💰 **Cash Offer Sequence**
1. Create New Sequence: "Cash Offer Follow-up"
2. Create 4 emails with these delays:
   - Email 1: Immediately (0 hours)
   - Email 2: 2 days delay
   - Email 3: 5 days delay
   - Email 4: 10 days delay

### 📋 **Lead Magnet Sequence**
1. Create New Sequence: "Foreclosure Education Series"
2. Create 6 emails with these delays:
   - Email 1: Immediately (0 hours)
   - Email 2: 2 days delay
   - Email 3: 5 days delay
   - Email 4: 8 days delay
   - Email 5: 12 days delay
   - Email 6: 14 days delay

---

## **Step 2: Create Tags for Lead Types**

Go to ConvertKit → Subscribers → Tags → Create New Tag:

1. **"Urgent-Foreclosure"** - For emergency foreclosure help requests
2. **"Cash-Offer-Lead"** - For calculator users wanting cash offers
3. **"Lead-Magnet"** - For checklist downloads
4. **"Exit-Intent"** - For exit popup captures
5. **"General-Contact"** - For main contact form submissions

---

## **Step 3: Set Up Automation Rules**

Go to ConvertKit → Automations → Rules → Create New Rule:

### **Rule 1: Urgent Foreclosure Trigger**
- **Trigger**: Subscriber is tagged "Urgent-Foreclosure"
- **Action**: Add to "Urgent Foreclosure - 5 Day Sequence"

### **Rule 2: Cash Offer Trigger**  
- **Trigger**: Subscriber is tagged "Cash-Offer-Lead"
- **Action**: Add to "Cash Offer Follow-up"

### **Rule 3: Lead Magnet Trigger**
- **Trigger**: Subscriber is tagged "Lead-Magnet" OR "Exit-Intent"
- **Action**: Add to "Foreclosure Education Series"

### **Rule 4: General Contact Trigger**
- **Trigger**: Subscriber is tagged "General-Contact"  
- **Action**: Add to "Foreclosure Education Series" (or create separate sequence)

---

## **Step 4: Update Google Apps Script for Tagging**

Your current Google Apps Script needs to be updated to add tags based on lead type:

```javascript
// Add this function to your Google Apps Script
function addToConvertKitWithTag(email, name, leadType) {
  var FORM_ID = '8430004';
  var API_KEY = 'Hh9PtQFOyWkQN4SZ3w0iXA';
  var url = 'https://api.convertkit.com/v3/forms/' + FORM_ID + '/subscribe';
  
  // Determine tag based on lead type
  var tags = [];
  switch(leadType) {
    case 'emergency_help':
    case 'foreclosure_urgent':
      tags = ['urgent-foreclosure'];
      break;
    case 'cash_offer_request':
      tags = ['cash-offer-lead'];
      break;
    case 'lead_magnet':
      tags = ['lead-magnet'];
      break;
    case 'exit_intent_popup':
      tags = ['exit-intent'];
      break;
    default:
      tags = ['general-contact'];
  }
  
  var payload = {
    api_key: API_KEY,
    email: email,
    first_name: name ? name.split(' ')[0] : '',
    tags: tags
  };
  
  // Rest of function stays the same...
}
```

---

## **Step 5: Copy Email Content to ConvertKit**

For each sequence, copy the email content from the markdown files:

### **Email Subject Line Format:**
- Use dynamic fields: `{{first_name}}`, `{{property_address}}`, etc.
- Keep subject lines under 50 characters for mobile
- Use emojis sparingly (1-2 max)

### **Email Body Formatting:**
- Use ConvertKit's visual editor
- Add proper spacing between sections
- Bold important points
- Use bullet points for lists
- Include call-to-action buttons for phone/text

### **Dynamic Field Mapping:**
Make sure these custom fields are created in ConvertKit:
- `property_address`
- `desired_price`
- `timeline`
- `property_condition`
- `property_type`

---

## **Step 6: Test the Complete Funnel**

### **Test Sequence:**
1. Submit each form type on your website
2. Check ConvertKit subscribers for new entries
3. Verify correct tags are applied
4. Confirm appropriate sequences start
5. Check email delivery and formatting

### **Testing Checklist:**
- [ ] Contact form → General Contact tag → Education sequence
- [ ] Calculator → Cash Offer tag → Cash Offer sequence  
- [ ] Lead magnet → Lead Magnet tag → Education sequence
- [ ] Exit popup → Exit Intent tag → Education sequence
- [ ] Urgent leads → Urgent tag → Urgent sequence

---

## **Step 7: Monitor and Optimize**

### **Key Metrics to Track:**
- **Open Rates**: Should be 25%+ (foreclosure niche typically higher)
- **Click Rates**: Should be 5%+ 
- **Unsubscribe Rate**: Should be under 2%
- **Conversion to Consultation**: Track how many book calls

### **A/B Testing:**
- Test different subject lines
- Test send times (9 AM vs 2 PM vs 6 PM)
- Test email length (shorter vs longer)
- Test call-to-action wording

---

## **Step 8: Compliance and Best Practices**

### **Required Elements:**
- [ ] Unsubscribe link in every email (ConvertKit auto-adds)
- [ ] Your business address in footer
- [ ] Clear sender identification
- [ ] Honest subject lines (no deceptive content)

### **Best Practices:**
- Send from a real name, not company name
- Use consistent "From" address
- Keep images minimal (text-focused)
- Mobile-responsive templates
- Test across email clients

---

## **Emergency Contact Information**

**If sequences aren't triggering:**
1. Check API keys are correct
2. Verify form ID is accurate  
3. Test Google Apps Script functions manually
4. Check ConvertKit automation rules are active
5. Verify webhook URLs are correct

**Support:**
- ConvertKit Help: help.convertkit.com
- Google Apps Script Docs: developers.google.com/apps-script

---

**Next Steps After Setup:**
1. Create downloadable foreclosure checklist PDF
2. Set up SMS integration for immediate responses  
3. Create landing pages for different lead types
4. Set up conversion tracking in Google Analytics
5. Plan monthly content calendar for ongoing emails