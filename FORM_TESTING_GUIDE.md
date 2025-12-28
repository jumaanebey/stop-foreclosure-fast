# Virtual Consultation Form Testing Guide

## Test Scenarios

### 1. Basic Form Submission Test
**Test Data:**
- Name: Test User
- Email: test@example.com
- Phone: (555) 123-4567
- County: Los Angeles
- Urgency: Urgent
- Device: Computer

**Expected Result:**
- Form submits successfully
- Data appears in Google Sheets
- Thank you message displays
- Analytics event fires

### 2. Mobile Device Test
- Test on smartphone
- Test on tablet
- Verify responsive design
- Check touch interactions

### 3. Error Handling Test
- Submit with missing required fields
- Test invalid email formats
- Test invalid phone numbers
- Verify error messages display

### 4. Analytics Verification
- Check Google Analytics for form events
- Verify lead tracking fires
- Confirm conversion goals work
- Test Facebook Pixel events

## Post-Test Actions
After successful testing:
1. Update Google Sheets permissions
2. Set up email notifications
3. Configure auto-responder
4. Test emergency contact flow