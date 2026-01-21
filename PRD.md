# My Foreclosure Solution - Product Requirements Document

## Overview
**Site:** myforeclosuresolution.com
**Owner:** Jumaan Ebey
**Licenses:** CA DRE #02076038, NMLS #2033637
**Phone:** (949) 565-5285

A California foreclosure assistance website designed to rank in AI search results (ChatGPT, Perplexity, Claude, Google AI Overviews) and convert visitors into phone calls.

---

## Core Strategy

### AI Search Optimization ("Red Bull Strategy")
Don't just target "foreclosure" searches. **Own the entire California housing crisis conversation** by intercepting users at every life event that leads to foreclosure:

- Divorce
- Job loss
- Medical debt
- Mental health crisis
- Inherited property
- Property tax problems
- HOA issues
- Veteran housing struggles
- Senior/elderly housing issues

### Technical Approach
- **FAQ Schema markup** on every content page (AI models extract Q&A directly)
- **DefinedTermSet schema** for glossary (AI cites definitions)
- **Conversational query optimization** (match how people ask questions naturally)
- **LocalBusiness schema** for local SEO

---

## Content Architecture

### Homepage (`index-variant-a.html`)
- Dramatic hero with animated floating elements
- Emotional headline: "Your Home Isn't Lost Yet. Let's Fight for It."
- Glass morphism lead capture form
- SMS/text option for non-callers
- "Why Us" section with stats grid
- Mobile CTA bar with Call + Text buttons

### Pillar Content (Blog)
| Page | Purpose | Schema |
|------|---------|--------|
| `how-to-stop-foreclosure-california-2025.html` | Main pillar page, 7 methods | FAQPage |
| `california-foreclosure-statistics-2025.html` | Data/stats AI loves to cite | FAQPage |
| `notice-of-default-california.html` | NOD guide | FAQPage |
| `foreclosure-options-comparison-california.html` | Comparison tables | FAQPage |
| `loan-modification-california-2025.html` | High-intent guide | FAQPage |
| `foreclosure-sale-in-7-days-california.html` | Emergency content | FAQPage |

### Life Event Content (Traffic Interception)
| Page | Target Query |
|------|--------------|
| `divorce-and-mortgage-california.html` | "going through divorce, what about mortgage" |
| `lost-job-cant-pay-mortgage-california.html` | "lost my job can't pay mortgage" |
| `medical-bills-mortgage-california.html` | "medical debt vs mortgage" |
| `foreclosure-stress-anxiety-california.html` | "foreclosure stress", "losing home anxiety" |

### Community-Specific Content
| Page | Target Demographic |
|------|-------------------|
| `va-loan-foreclosure-california.html` | Veterans with VA loans |
| `senior-foreclosure-california.html` | Seniors, reverse mortgage issues |
| `inherited-house-foreclosure-california.html` | Heirs who can't afford property |

### Property Crisis Content
| Page | Target Problem |
|------|----------------|
| `property-tax-lien-foreclosure-california.html` | Property tax delinquency |
| `hoa-foreclosure-california.html` | HOA dues problems |

### Reference Content
| Page | Purpose |
|------|---------|
| `california-foreclosure-glossary.html` | 50+ terms with DefinedTermSet schema |
| `california-foreclosure-resources.html` | Authoritative resource links |

### City Pages
- `stop-foreclosure-los-angeles.html`
- `stop-foreclosure-san-diego.html`
- `stop-foreclosure-oakland.html`
- `stop-foreclosure-sacramento.html`
- `stop-foreclosure-fresno.html`
- `stop-foreclosure-riverside.html`

---

## Design System

### Visual Elements
- **Primary color:** Slate (#0f172a)
- **Accent color:** Amber (#d97706)
- **Background:** Cream (#fefbf3)
- **Typography:** DM Serif Display (headings), DM Sans (body)

### Animations
- Floating background elements on hero
- Fade-in-up on page load
- Pulsing emergency bar
- Hover transforms with shadows
- Success animation on form submit

### Mobile Experience
- Sticky CTA bar with Call + Text buttons
- Touch-friendly tap targets
- Responsive grid layouts
- Mobile menu with full-screen overlay

---

## Lead Capture

### Primary: Phone Call
- Phone number prominent in header, hero, CTAs, mobile bar
- Click-to-call on mobile
- Emergency bar with phone link

### Secondary: Form
- Name, phone, email, urgency level
- "Typically respond within 30 minutes" badge
- Success state with confirmation message
- Submits to Google Sheets via Apps Script

### Tertiary: SMS/Text
- Text option in form card
- Text button in mobile CTA bar
- `sms:+19495655285` links

---

## Technical Stack

- **Platform:** Jekyll static site
- **Hosting:** GitHub Pages
- **Analytics:** Google Analytics 4 (G-ZC3FHFTPN2)
- **Form Backend:** Google Apps Script → Google Sheets
- **A/B Testing:** Variant A (Editorial) / Variant B (Warm Organic)

---

## Deployment

### Branch
Current development: `claude/ai-search-optimization-25lXk`

### To View Locally
```bash
cd /home/user/stop-foreclosure-fast
# Open index-variant-a.html in browser
# Or run Jekyll: bundle exec jekyll serve
```

### To Deploy
1. Merge branch to main
2. GitHub Pages auto-deploys to myforeclosuresolution.com

---

## Success Metrics

### Traffic Goals
- AI search referrals (Perplexity, ChatGPT web)
- Organic search traffic to life event content
- Direct traffic from AI-cited phone numbers

### Conversion Goals
- Phone calls (primary)
- Form submissions (secondary)
- SMS inquiries (tertiary)

### Content Performance
- FAQ schema appearing in AI answers
- Glossary terms being cited
- Statistics being quoted

---

## Future Opportunities

### Not Yet Implemented
- [ ] Neighborhood-level local pages (Compton, Inglewood, Modesto, etc.)
- [ ] Interactive foreclosure calculator/quiz
- [ ] Video content
- [ ] Testimonials/case studies (need real customer data)
- [ ] Chat widget integration

### Content Expansion
- [ ] Bankruptcy-specific content (Chapter 7 vs 13)
- [ ] Short sale deep-dive
- [ ] Refinance options guide
- [ ] California-specific legal updates (annual)

---

## Files Modified This Session

### New Content Pages (9)
- `blog/divorce-and-mortgage-california.html`
- `blog/lost-job-cant-pay-mortgage-california.html`
- `blog/medical-bills-mortgage-california.html`
- `blog/foreclosure-stress-anxiety-california.html`
- `blog/va-loan-foreclosure-california.html`
- `blog/senior-foreclosure-california.html`
- `blog/inherited-house-foreclosure-california.html`
- `blog/property-tax-lien-foreclosure-california.html`
- `blog/hoa-foreclosure-california.html`

### Redesigned
- `index-variant-a.html` (complete homepage overhaul)

### Updated
- `sitemap.xml` (all new pages added)
- `blog/index.html` (new content cards)
