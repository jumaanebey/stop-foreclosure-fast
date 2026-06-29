# HomeIQ Academy — Handoff Document

## Priority Bug: Email Login Opens In-App Browser

**Problem:** When a user receives an email (magic link, OTP, notification) and taps the link, it opens in the email app's in-app browser (e.g., Gmail WebView). This creates a separate session that doesn't carry over to Safari or the native app.

**Expected behavior:**
1. If HomeIQ Academy app is installed → deep link opens the app directly
2. If app is not installed → opens in Safari (not the email app's WebView)

**What needs to happen:**
- Implement iOS Universal Links (apple-app-site-association file) so email links open the native app
- Add `apple-app-site-association` to `homeiqacademy.com/.well-known/`
- Configure Associated Domains in Xcode (`applinks:homeiqacademy.com`)
- Update Supabase email templates to use the website URL (not Supabase's own URL) as the redirect
- Test with Gmail, Apple Mail, and Outlook on iOS
- Fallback: if app not installed, Safari opens the web version

**Related context:**
- App is live on App Store: https://apps.apple.com/app/homeiq-academy/id6760271654
- Bundle ID: `com.homeiqacademy.app`
- Capacitor config loads from `homeiqacademy.com` (server.url)
- Current deep link scheme: `com.homeiqacademy.app` (in Info.plist CFBundleURLSchemes)
- Google OAuth relay already exists but has separate WKWebView issues (see memory)

**This is a known iOS pattern** — Apple Universal Links are the standard solution. Do NOT try custom URL schemes (`homeiqacademy://`) as they don't work from email clients.

---

## Other Pending Items (from CLAUDE-TODAY.md)

- Set up jumaanebey@homeiqacademy.com (Cloudflare email routing)
- Send Anthropic follow-up email
- Google Play submission (Android Studio build)
- Top of funnel campaign — broker outreach + direct to buyer
- Verify subscription enforcement end-to-end
- Test Daily Pick API, milestone celebrations
- YouTube video embed card type
- n8n automations (drip sequences, lesson reminders)
- Twilio SMS (milestone texts)
- Trademark HomeIQ Academy (USPTO Class 41 + 42)
- Fix Canva infographic PNGs
- Upload brokerage logos
