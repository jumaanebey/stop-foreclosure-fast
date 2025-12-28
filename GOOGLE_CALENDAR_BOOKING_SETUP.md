# Google Calendar Appointment Scheduling Setup

## Overview
Use Google Calendar's built-in appointment scheduling to let leads book virtual consultations with automatic Google Meet video links.

---

## Step 1: Enable Appointment Scheduling

1. Go to [calendar.google.com](https://calendar.google.com)
2. Click the **gear icon** (Settings) → **Settings**
3. Scroll to **Appointment schedules** section
4. Make sure it's enabled for your account

---

## Step 2: Create Your Appointment Schedule

1. In Google Calendar, click **+ Create** button
2. Select **Appointment schedule**
3. Fill in the details:

### Basic Settings
| Field | Value |
|-------|-------|
| **Title** | Free Foreclosure Consultation |
| **Duration** | 30 minutes |
| **Location** | Google Meet (auto-generated) |

### Availability
| Field | Setting |
|-------|---------|
| **Days** | Monday - Friday |
| **Hours** | 6:00 PM - 8:00 PM PST |
| **Buffer time** | 15 minutes between appointments |
| **Minimum notice** | 2 hours |
| **Max per day** | 3 appointments |

### Booking Form Questions
Add these required fields:
1. **Name** (required)
2. **Email** (required - auto-filled)
3. **Phone Number** (required)
4. **Property Address** (required)
5. **How urgent is your situation?** (dropdown)
   - Auction in less than 7 days
   - Auction in less than 30 days
   - Auction in 30-90 days
   - No auction date yet
6. **Briefly describe your situation** (text area)

---

## Step 3: Get Your Booking Link

After creating the schedule:
1. Click on the appointment schedule in your calendar
2. Click **Open booking page**
3. Copy the URL - it looks like:
   ```
   https://calendar.google.com/calendar/appointments/schedules/[YOUR_SCHEDULE_ID]
   ```

---

## Step 4: Customize Booking Page

1. Click **Sharing settings** on your appointment schedule
2. Add your branding:
   - Profile photo
   - Description: "Schedule a free, confidential consultation with a licensed California foreclosure specialist. We'll discuss your options and create a personalized action plan."

3. Set confirmation settings:
   - Send email confirmations
   - Include Google Meet link
   - Add calendar invitation

---

## Step 5: Set Up Email Notifications

In appointment schedule settings:
1. Enable **Email reminders** to attendees:
   - 24 hours before
   - 1 hour before

2. Enable notifications to yourself:
   - Immediately when booked
   - Morning summary of day's appointments

---

## Your Booking Link

Once set up, your link will be:
```
https://calendar.google.com/calendar/appointments/schedules/[YOUR_ID]
```

**Short link option:** Create a redirect at:
```
myforeclosuresolution.com/book → [Your Google Calendar link]
```

---

## Integration with Website

Add this button to your website (I'll add this for you):

```html
<a href="YOUR_BOOKING_LINK"
   target="_blank"
   class="book-consultation-btn">
   📅 Book Free Video Consultation
</a>
```

---

## Google Meet Benefits

- **Free** - No Zoom subscription needed
- **Automatic** - Meet link created for each booking
- **Integrated** - Shows in both calendars
- **Recorded** - Option to record consultations
- **Screen share** - Show documents during call

---

## Checklist

- [ ] Create appointment schedule in Google Calendar
- [ ] Set availability (M-F, 9-5 PST)
- [ ] Add booking form questions
- [ ] Test booking flow yourself
- [ ] Copy booking link
- [ ] Add to website (I'll do this)
- [ ] Test end-to-end

---

## Once You Have Your Link

Reply with your Google Calendar appointment booking link and I'll:
1. Add a "Book Consultation" button to the homepage
2. Add booking links to all email sequences
3. Add to thank-you pages
4. Add to the mobile CTA bar

---

**Setup Time:** ~10 minutes
**Cost:** Free (included with Google Workspace or personal Gmail)
