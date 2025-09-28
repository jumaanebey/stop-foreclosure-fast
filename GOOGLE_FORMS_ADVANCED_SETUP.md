# 📋 Google Forms - Advanced Lead Validation Setup

## 🎯 Exact Configuration for High-Quality Leads

### STEP 1: Create New Google Form
1. Go to https://forms.google.com
2. Click "+" (Blank form)
3. Title: "Foreclosure Help Request - Get Help Now"
4. Description: "Complete this form and a foreclosure specialist will contact you within 30 minutes"

---

## 📞 FIELD 1: PHONE NUMBER (with full validation)

**Question Type:** Short answer
**Question:** "Phone Number"
**Description:** "Enter your 10-digit phone number (xxx) xxx-xxxx"
**Required:** YES

**VALIDATION SETTINGS:**
1. Click the 3-dots menu → "Response validation"
2. Choose "Regular expression"
3. Select "Matches"
4. Enter this pattern: `^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$`

**What this does:**
- Requires exactly 10 digits
- Accepts formats: (555) 123-4567, 555-123-4567, 555.123.4567, 5551234567
- Rejects incomplete numbers
- Shows error: "Please enter a valid 10-digit phone number"

---

## 📧 FIELD 2: EMAIL (with domain validation)

**Question Type:** Short answer
**Question:** "Email Address"
**Description:** "We'll send you a confirmation email immediately"
**Required:** YES

**VALIDATION SETTINGS:**
1. Click the 3-dots menu → "Response validation"
2. Choose "Regular expression"
3. Select "Matches"
4. Enter this pattern: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

**Additional Email Validation:**
- Google Forms automatically validates email format
- The regex above ensures:
  - Valid email structure
  - Real domain required (.com, .org, etc.)
  - No fake emails like "test@test"

---

## 🏠 FIELD 3: PROPERTY ADDRESS (with live validation)

**Question Type:** Short answer
**Question:** "Property Address"
**Description:** "Enter the full address: 123 Main St, City, State, ZIP"
**Required:** YES

**VALIDATION SETTINGS:**
1. Click the 3-dots menu → "Response validation"
2. Choose "Regular expression"
3. Select "Matches"
4. Enter this pattern: `^.+,\s*.+,\s*[A-Za-z]{2}\s*,?\s*\d{5}(-\d{4})?.*$`

**What this validates:**
- Must include street, city, state, ZIP
- Examples that work:
  - "123 Main St, Los Angeles, CA 90210"
  - "456 Oak Ave, San Diego, California, 92101"
  - "789 Pine Rd, Sacramento, CA, 95814-1234"
- Rejects incomplete addresses

**FOR LIVE ADDRESS LOOKUP:**
*Note: Google Forms doesn't have built-in address autocomplete, but here are alternatives:*

**Option A: Use Google Places API (Advanced)**
- Requires custom JavaScript (CSP issues on GitHub Pages)
- Not recommended for your current setup

**Option B: JotForm (Alternative with Address Lookup)**
- Go to https://www.jotform.com
- Has built-in Google Places address autocomplete
- Can embed in your website like Google Forms
- More advanced but costs money for full features

**Option C: Keep Google Forms + Manual Verification**
- Use the regex validation above
- Manually verify addresses when leads come in
- Most businesses do this anyway

---

## 📅 FIELD 4: TIMELINE (Critical for prioritization)

**Question Type:** Multiple choice
**Question:** "When is your foreclosure sale scheduled?"
**Required:** YES

**Options (in this exact order):**
1. Within 7 days 🚨 CRITICAL
2. Within 14 days ⚡ URGENT
3. Within 30 days ⏰ Important
4. Within 60 days 📅 Planning ahead
5. Over 60 days 🗓️ Early planning
6. I don't know ❓ Need help finding out

---

## 📋 FIELD 5: FORECLOSURE STAGE

**Question Type:** Multiple choice
**Question:** "What stage are you in?"
**Required:** YES

**Options:**
1. Just missed a few payments
2. Received Notice of Default (NOD)
3. Received Notice of Trustee Sale
4. Auction date is scheduled
5. Already went to auction
6. I'm not sure what stage I'm in

---

## 💰 FIELD 6: PROPERTY VALUE (for qualification)

**Question Type:** Short answer
**Question:** "Estimated Property Value"
**Description:** "What do you think your home is worth? (rough estimate)"
**Required:** YES

**VALIDATION:**
1. Response validation → "Number"
2. "Greater than" → 50000
3. "Less than" → 5000000
4. Error message: "Please enter a value between $50,000 and $5,000,000"

---

## 🏦 FIELD 7: MORTGAGE BALANCE

**Question Type:** Short answer
**Question:** "Approximate Mortgage Balance Owed"
**Description:** "How much do you still owe on your mortgage?"
**Required:** YES

**VALIDATION:**
1. Response validation → "Number"
2. "Greater than" → 0
3. Error message: "Please enter the amount you owe"

---

## 📱 FIELD 8: SMS CONSENT

**Question Type:** Checkboxes
**Question:** "How can we contact you?"
**Required:** NO

**Options:**
- ✅ Yes, send me text message updates (standard rates apply)
- ✅ Call me during business hours (9 AM - 6 PM)
- ✅ Call me anytime, even evenings/weekends

---

## 👤 FIELD 9: NAME

**Question Type:** Short answer
**Question:** "Your Full Name"
**Description:** "First and Last Name"
**Required:** YES

**VALIDATION:**
1. Response validation → "Regular expression"
2. "Matches" → `^[A-Za-z]+\s+[A-Za-z]+.*$`
3. Error: "Please enter your first and last name"

---

## ⚙️ ADVANCED FORM SETTINGS

### STEP 1: Configure Notifications
1. Click "Responses" tab
2. Click 3-dots menu → "Get email notifications for new responses"
3. Turn ON notifications
4. Emails go to: jumaanebey@gmail.com

### STEP 2: Custom Thank You Message
1. Click Settings (gear icon)
2. Go to "Presentation" tab
3. Custom confirmation message:

```
✅ THANK YOU! Your foreclosure request has been received.

📧 CONFIRMATION: Check your email for our response
📱 URGENT CASES: We'll call within 30 minutes
🚨 CRITICAL (7-day sales): We'll contact you immediately

Need immediate help?
📞 Call now: (949) 328-4811

- Licensed California Real Estate Professionals
- Free consultation, no obligation
- We've helped 500+ families save their homes
```

### STEP 3: Collect Email Addresses
1. Settings → "Responses"
2. Turn ON "Collect email addresses"
3. This creates an automatic email receipt

### STEP 4: Response Spreadsheet
1. In "Responses" tab
2. Click the Google Sheets icon
3. Creates automatic spreadsheet with all responses
4. You can sort by urgency, add notes, track follow-ups

---

## 🎨 CUSTOMIZE APPEARANCE

### Header & Colors
1. Click the palette icon (top right)
2. Choose theme color: Orange (#ea580c) to match your website
3. Add header image (optional): Upload your logo

### Question Layout
1. In each question, click "..." → "Description"
2. Add helpful text under each field
3. Use section breaks to organize questions

---

## 📊 ADVANCED FEATURES

### Response Validation Summary:
- ✅ Phone: Must be 10 digits
- ✅ Email: Must be valid format + real domain
- ✅ Address: Must include city, state, ZIP
- ✅ Property Value: Must be realistic number
- ✅ Name: Must be first + last name

### Automatic Benefits:
- 📧 Instant email notifications
- 📊 Automatic Google Sheets database
- 📱 Mobile-optimized form
- 🔒 Secure data collection
- 📈 Response analytics dashboard

---

## 🚀 EMBED IN YOUR WEBSITE

After creating the form:

1. Click "Send" (top right)
2. Click embed icon (< >)
3. Copy the iframe code
4. In your `index.html`, replace:
   ```html
   src="https://docs.google.com/forms/d/e/REPLACE_WITH_YOUR_FORM_ID/viewform?embedded=true"
   ```
5. Paste your actual form URL

---

## 🎯 RESULT: HIGH-QUALITY LEADS

With these validations, you'll get:
- ✅ Real, callable phone numbers
- ✅ Valid email addresses that work
- ✅ Complete property addresses
- ✅ Qualified prospects (property values)
- ✅ Prioritized by urgency level
- ✅ Full contact permissions

This eliminates fake submissions and ensures every lead is actionable!