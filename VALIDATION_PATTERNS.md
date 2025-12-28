# 🔧 Google Forms Validation Patterns - Copy & Paste

## 📞 PHONE NUMBER VALIDATION
**Pattern:** `^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$`
**Accepts:**
- (555) 123-4567
- 555-123-4567
- 555.123.4567
- 5551234567
**Rejects:** Incomplete numbers, letters, international formats

---

## 📧 EMAIL VALIDATION
**Pattern:** `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
**Accepts:**
- john@gmail.com
- mary.smith@company.co.uk
- lead123@foreclosure-help.org
**Rejects:** No @ symbol, no domain, fake domains

---

## 🏠 ADDRESS VALIDATION
**Pattern:** `^.+,\s*.+,\s*[A-Za-z]{2}\s*,?\s*\d{5}(-\d{4})?.*$`
**Accepts:**
- 123 Main St, Los Angeles, CA 90210
- 456 Oak Ave, San Diego, California, 92101
- 789 Pine Rd, Sacramento, CA, 95814-1234
**Rejects:** Incomplete addresses missing city/state/zip

---

## 👤 FULL NAME VALIDATION
**Pattern:** `^[A-Za-z]+\s+[A-Za-z]+.*$`
**Accepts:**
- John Smith
- Mary Jane Johnson
- José García-Martinez
**Rejects:** Single names, numbers, just first name

---

## 💰 PROPERTY VALUE VALIDATION
**Type:** Number
**Greater than:** 50000
**Less than:** 5000000
**Accepts:** $50,000 to $5,000,000
**Rejects:** Unrealistic values, letters

---

## 🚀 QUICK SETUP STEPS:

1. **Create form** at https://forms.google.com
2. **Add question** → Choose "Short answer"
3. **Click 3-dots** → "Response validation"
4. **Select "Regular expression"** → "Matches"
5. **Copy/paste pattern** from above
6. **Add custom error message**
7. **Make required** if needed

## 📋 COPY-PASTE ERROR MESSAGES:

- **Phone:** "Please enter a valid 10-digit phone number like (555) 123-4567"
- **Email:** "Please enter a valid email address"
- **Address:** "Please enter complete address: Street, City, State, ZIP"
- **Name:** "Please enter your first and last name"
- **Property Value:** "Please enter a realistic property value between $50,000 and $5,000,000"

## 🎯 RESULT: ZERO FAKE LEADS!

These patterns eliminate:
- ❌ Fake phone numbers (555-0000, 123-4567)
- ❌ Invalid emails (test@test, no domain)
- ❌ Incomplete addresses (just "123 Main St")
- ❌ Single names or fake names
- ❌ Unrealistic property values ($1 or $999,999,999)

**Every submission will be a high-quality, actionable lead!**