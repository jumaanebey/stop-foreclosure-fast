# Chrome - Do This Now

**Date:** January 8, 2026
**Goal:** Get the AI Guide button live on the website

---

## Step 1: Deploy Website to Hostinger (5 min)

The index.html file has been updated with the Gem button. It needs to be uploaded to Hostinger.

### Option A: Hostinger File Manager
1. Go to **hpanel.hostinger.com** → Log in
2. Click **Files** → **File Manager**
3. Navigate to **public_html**
4. Upload (replace) the file: `/Users/jumaanebey/Documents/stop-foreclosure-fast/index.html`
5. Done!

### Option B: Hostinger Git (if connected)
1. Go to **hpanel.hostinger.com** → **Git**
2. Click **Pull** to sync from GitHub
3. The repo was just pushed with the Gem button

### Option C: FTP (if you use FileZilla)
1. Connect to Hostinger FTP
2. Upload `index.html` to `public_html/`

---

## Step 2: Verify It Works

1. Go to **https://myforeclosuresolution.com**
2. Hard refresh (Cmd+Shift+R)
3. You should see a new button below the main CTAs:

   **🤖 Not sure if we can help? Chat with our AI guide first**

4. Click it - should open your Foreclosure Guide Gem

---

## Step 3: Test the Gem Flow

Click the button and test these scenarios:

| Test | What to Say | Expected Result |
|------|-------------|-----------------|
| Hot Lead | "My auction is in 5 days, I have $200k equity" | Urgent routing to call (949) 565-5285 |
| Warm Lead | "I got an NOD, sale in 2 months" | Education + soft handoff |
| Cold Lead | "Just exploring, no letters yet" | Resources + come back later |

---

## What Was Done (By Claude Code)

- [x] Built Foreclosure Guide Gem in Gemini
- [x] Tested with simulated lead (Maria)
- [x] Got shareable link
- [x] Added button to index.html hero section
- [x] Committed and pushed to GitHub
- [ ] **YOU:** Deploy to Hostinger (Step 1 above)

---

## Files Changed

```
/Users/jumaanebey/Documents/stop-foreclosure-fast/index.html
```

Line ~1360-1366 now contains:
```html
<!-- AI Guide CTA -->
<div style="text-align: center; margin-top: 10px;">
    <a href="https://gemini.google.com/gem/1xuCe4Dc1_dCqJeAK-AUA68mgmMUauf_I?usp=sharing" target="_blank" ...>
        🤖 Not sure if we can help? Chat with our AI guide first
    </a>
</div>
```

---

## After Deployment - Optional Next Steps

1. **Add Gem to social media bios** (Instagram, TikTok, Facebook)
2. **Test mobile experience** of the button
3. **Monitor Gem conversations** in Gemini

---

**Questions?** Ask Claude Code.
