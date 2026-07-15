# Website Improvement Tasks — My Foreclosure Solution

Context: This is a conversion-focused landing page (`index-variant-a.html`) for a
California foreclosure-help service run by a solo licensed professional
(NMLS #2033637, CA DRE #02076038). The goal of these changes is to increase
trust and messaging consistency without introducing unverifiable claims.

Work through the tasks below in order. After each task, keep the existing visual
design, fonts, and color scheme (serif headlines + warm orange accent). Do not
introduce new dependencies. Preserve all existing license-number displays.

---

## 1. Unify the voice to first person ("I")

The copy currently mixes "I" (e.g. "I started this company", "work directly
with me") with "we/us/our" (e.g. "We listen without judgment", "Why Families
Trust Us"). Since this is a solo licensed professional, standardize on the
personal first-person voice throughout.

- Replace "we/us/our" phrasing with "I/me/my" wherever it refers to the service
  provider. Examples:
  - "Three Steps to Peace of Mind" intro: "We make a confusing process simple"
    → "I make a confusing process simple".
  - "We listen without judgment" → "I listen without judgment".
  - "We analyze your specific situation" → "I analyze your specific situation".
  - "Why Families Trust Us With Their Biggest Asset" → keep "Us"/"Me" consistent
    with whatever headline decision you make, but ensure the body copy matches.
- Do NOT change legally-reviewed disclaimer text in the footer.
- Leave the phrase "Work Directly With Me" as-is (already correct).

## 2. Add a real "About / Meet Your Advisor" section

Add a new section between the "Three Steps" section and the "Why Families Trust
Us" section. It should support a real name, headshot photo, and short bio, since
the whole pitch is "you can actually reach a real person."

- Create a two-column layout: photo on one side, text on the other (stack on
  mobile).
- Add a placeholder image `assets/advisor-photo.jpg` with descriptive alt text
  ("Portrait of [Advisor Name], licensed California foreclosure advisor").
- Include placeholder copy fields clearly marked with `TODO`:
  - `TODO: Advisor full name`
  - `TODO: 2–3 sentence personal bio / why I started this`
  - `TODO: License display (NMLS / CA DRE) — reuse existing badge styling`
- Match existing card/section styling.

## 3. Add a testimonials section (structure only, no fake reviews)

Create a new "What Homeowners Say" section before the final CTA. Because there
are no real testimonials yet, build the layout but leave clearly-marked
placeholders — do NOT invent testimonials.

- Build a responsive 2–3 card grid.
- Each card: quote text, client first name + last initial, and optional
  city/county.
- Wrap the entire section in an HTML comment:
  `<!-- TODO: Enable this section once real, permission-approved testimonials
  exist. Do not use fabricated reviews. -->`
- Keep it hidden (e.g. `hidden` attribute or `display:none`) until real content
  is added, so it never ships empty.

## 4. Revise questionable stats

In the stats band (currently: "1:1 Personal Consultations", "58 CA Counties
Served", "$0 Upfront Cost", "100% Confidential"):

- Replace "58 CA Counties Served" — this just restates that CA has 58 counties
  and reads as filler. Swap for a concrete, defensible metric with a `TODO`
  placeholder for the real number, e.g.:
  - `TODO: Families helped` or `TODO: Years of experience`.
- Keep "$0 Upfront Cost" and "100% Confidential".
- Add an HTML comment reminding that all stats must be truthful and
  substantiable.

## 5. Verify internal links / pages exist

The nav and footer link to: How It Works, FAQ, Free Guide, Resources, Blog,
Emergency Help, Glossary, Contact, Privacy Policy, Disclaimer, Terms of Service,
and the three resource guides ("How to Stop Foreclosure in California (2025)",
"California Foreclosure Timeline", "Can I Sell During Foreclosure?").

- Audit every `href` in the file. For each link, confirm the target file exists
  in the project.
- Produce a report listing which links resolve and which are broken/empty
  (dead `#` anchors, missing files).
- For any missing page, create a minimal stub file with a heading and a
  `TODO: content` marker, and wire the link to it, so no link 404s.

## 6. Form UX hardening

For the "Request Your Private Consultation" form:

- Ensure phone links use `tel:` and text/"Text us" uses `sms:` so they are
  click-to-call on mobile.
- Add visible client-side validation and clear success and error states on
  submit (no silent failures).
- Add `aria-label`/`<label>` associations for every field for accessibility.
- Do NOT add any analytics/tracking or third-party scripts as part of this task.

## 7. Mobile / responsive check

- Verify the hero's two-column layout (headline + form) stacks cleanly on
  mobile, with the form still easily reachable.
- Confirm the new About and testimonials sections stack correctly.
- Check tap target sizes for the phone/CTA buttons.

## 8. Compliance safety note (do not auto-edit — flag only)

Foreclosure-consultant advertising is heavily regulated in California. Do NOT
rewrite legal/marketing claims on your own. Instead, output a short list of
phrases that a compliance reviewer should check, including at minimum:
"Let's Fight for It", "No upfront fees, ever", and any outcome-suggesting copy.
Leave the copy as-is and just surface the list.

---

When finished, output a summary of: files changed, new files created, links
fixed, and every remaining `TODO` placeholder that needs real content from the
site owner.
