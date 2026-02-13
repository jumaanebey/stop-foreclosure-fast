#!/usr/bin/env python3
"""
Additional Video Scripts - FAQ, City-Specific, Deep Dives
"""

# Import the main generator
from video_generator_pro import create_video, create_vertical, OUTPUT_DIR
import os

# ============================================================
# FAQ VIDEOS - Quick answers to common questions
# ============================================================

FAQ_SCRIPTS = {
    "faq-how-long-foreclosure": {
        "title": "How Long Does Foreclosure Take",
        "sections": [
            {
                "title": "California Foreclosure Timeline",
                "points": ["Non-judicial state", "180-200 days typical", "Starts after missed payments"],
                "dialogue": "How long does foreclosure take in California? The entire process typically takes 180 to 200 days from your first missed payment to the auction."
            },
            {
                "title": "The Key Milestones",
                "points": ["Day 1-120: Pre-foreclosure", "Day 120: Notice of Default", "Day 210+: Notice of Sale"],
                "dialogue": "Here are the key milestones. For the first 120 days, you're in pre-foreclosure. Then comes the Notice of Default, giving you 90 more days. Finally, the Notice of Sale sets your auction date."
            },
            {
                "title": "You Have Time to Act",
                "points": ["Don't panic", "Explore your options", "Get help early"],
                "dialogue": "The good news? You have time to act. Don't panic. Use this time to explore loan modification, short sale, or selling your home. The earlier you act, the more options you have."
            },
            {
                "title": "Get Free Help",
                "points": ["Free consultation", "No obligation"],
                "dialogue": "Need help navigating the timeline? Contact My Foreclosure Solution for a free consultation. We'll explain your options and help you take action."
            }
        ]
    },
    "faq-can-stop-auction": {
        "title": "Can I Stop a Foreclosure Auction",
        "sections": [
            {
                "title": "Yes You Can Stop It",
                "points": ["Multiple ways to stop", "Even days before auction", "Act fast"],
                "dialogue": "Can you stop a foreclosure auction? Yes, you absolutely can. Even if your auction is just days away, you still have options."
            },
            {
                "title": "Option 1 - Pay What You Owe",
                "points": ["Reinstate your loan", "Pay all missed payments", "Plus fees and costs"],
                "dialogue": "Option one: reinstate your loan. Pay all missed payments plus fees and costs. In California, you can do this up to 5 days before the auction."
            },
            {
                "title": "Option 2 - File Bankruptcy",
                "points": ["Automatic stay", "Stops auction immediately", "Consult an attorney"],
                "dialogue": "Option two: file for bankruptcy. This triggers an automatic stay that stops the auction immediately. But this has serious consequences, so consult an attorney first."
            },
            {
                "title": "Option 3 - Sell Fast",
                "points": ["Cash buyers close quickly", "Can close before auction", "Walk away with money"],
                "dialogue": "Option three: sell your home fast to a cash buyer. We can close in as little as 7 days, often before your auction date. You walk away with money instead of nothing."
            },
            {
                "title": "Time is Critical",
                "points": ["Call us today", "Free consultation", "We act fast"],
                "dialogue": "Time is critical. The closer you are to auction, the fewer options you have. Call My Foreclosure Solution today. We specialize in stopping foreclosures fast."
            }
        ]
    },
    "faq-hurt-credit": {
        "title": "How Does Foreclosure Hurt Credit",
        "sections": [
            {
                "title": "Foreclosure Credit Impact",
                "points": ["Major credit damage", "Stays on report 7 years", "100-150 point drop typical"],
                "dialogue": "How does foreclosure hurt your credit? A foreclosure can drop your credit score by 100 to 150 points or more. And it stays on your credit report for 7 years."
            },
            {
                "title": "Future Consequences",
                "points": ["Hard to get new mortgage", "Higher interest rates", "May affect jobs and rentals"],
                "dialogue": "The consequences go beyond your score. You'll have trouble getting a new mortgage for years. When you do qualify, you'll pay higher interest rates. Some employers and landlords check credit too."
            },
            {
                "title": "Better Alternatives",
                "points": ["Short sale - less damage", "Deed in lieu - negotiable", "Sell fast - avoid foreclosure"],
                "dialogue": "The good news? There are alternatives that hurt your credit less. A short sale, deed in lieu, or selling your home before foreclosure all look better on your credit than a foreclosure."
            },
            {
                "title": "Protect Your Credit",
                "points": ["Act before foreclosure hits", "Free consultation", "We can help"],
                "dialogue": "Want to protect your credit? Act before the foreclosure is complete. Contact My Foreclosure Solution for a free consultation. We'll help you find the best option for your situation."
            }
        ]
    },
    "faq-keep-my-home": {
        "title": "Can I Keep My Home in Foreclosure",
        "sections": [
            {
                "title": "Yes You May Keep It",
                "points": ["Several options exist", "Depends on your situation", "Act quickly"],
                "dialogue": "Can you keep your home during foreclosure? Yes, there are several ways to keep your home, but you need to act quickly."
            },
            {
                "title": "Loan Modification",
                "points": ["Change loan terms", "Lower payments", "Most common solution"],
                "dialogue": "The most common way is a loan modification. Your lender changes your loan terms to make payments affordable. This might mean a lower interest rate or longer loan term."
            },
            {
                "title": "Forbearance Agreement",
                "points": ["Temporary payment reduction", "Catch up over time", "Good for temporary hardship"],
                "dialogue": "Another option is forbearance. Your lender temporarily reduces or pauses payments while you get back on your feet. This works well for temporary hardship like job loss."
            },
            {
                "title": "Reinstatement",
                "points": ["Pay all missed payments", "Plus fees and costs", "Loan continues normally"],
                "dialogue": "You can also reinstate your loan by paying all missed payments plus fees. Once you're caught up, your loan continues as normal."
            },
            {
                "title": "Get Help Today",
                "points": ["Free consultation", "Explore all options", "We're here to help"],
                "dialogue": "Not sure which option is right for you? Contact My Foreclosure Solution for a free consultation. We'll review your situation and help you explore every option to keep your home."
            }
        ]
    }
}

# ============================================================
# CITY-SPECIFIC VIDEOS - Local SEO
# ============================================================

CITY_SCRIPTS = {
    "los-angeles-foreclosure": {
        "title": "Stop Foreclosure in Los Angeles",
        "sections": [
            {
                "title": "LA Homeowners Have Options",
                "points": ["High property values help", "Strong buyer demand", "Multiple solutions"],
                "dialogue": "If you're facing foreclosure in Los Angeles, you have more options than you might think. LA's high property values and strong buyer demand work in your favor."
            },
            {
                "title": "LA Market Advantage",
                "points": ["Homes sell quickly", "Cash buyers active", "Equity often available"],
                "dialogue": "Los Angeles has one of the strongest real estate markets in California. Homes sell quickly, cash buyers are active, and many homeowners have significant equity even in foreclosure."
            },
            {
                "title": "Your Options in LA",
                "points": ["Loan modification", "Short sale", "Sell for cash", "Keep your equity"],
                "dialogue": "Your options include loan modification to stay in your home, short sale if you're underwater, or selling fast for cash to keep your equity. We help LA homeowners every day."
            },
            {
                "title": "Local Help Available",
                "points": ["We know LA market", "Free consultation", "Fast solutions"],
                "dialogue": "At My Foreclosure Solution, we specialize in helping Los Angeles homeowners. We know the local market and can provide fast solutions. Call us for a free consultation today."
            }
        ]
    },
    "san-diego-foreclosure": {
        "title": "Stop Foreclosure in San Diego",
        "sections": [
            {
                "title": "San Diego Foreclosure Help",
                "points": ["Beautiful city, tough situation", "You have options", "We can help"],
                "dialogue": "Facing foreclosure in San Diego? You're not alone, and you have options. San Diego's strong real estate market gives you leverage."
            },
            {
                "title": "San Diego Market Benefits",
                "points": ["High demand area", "Military and tech buyers", "Strong property values"],
                "dialogue": "San Diego benefits from high demand due to military bases, tech companies, and perfect weather. This means your home likely has value, even in foreclosure."
            },
            {
                "title": "Solutions for SD Homeowners",
                "points": ["Sell before auction", "Keep your equity", "Avoid credit damage"],
                "dialogue": "We help San Diego homeowners sell before auction, keep their equity, and avoid the credit damage of foreclosure. Even if you're behind on payments, options exist."
            },
            {
                "title": "Free San Diego Consultation",
                "points": ["Local experts", "No obligation", "Call today"],
                "dialogue": "Get a free consultation from experts who know the San Diego market. At My Foreclosure Solution, we've helped homeowners across San Diego County. Call us today."
            }
        ]
    },
    "sacramento-foreclosure": {
        "title": "Stop Foreclosure in Sacramento",
        "sections": [
            {
                "title": "Sacramento Foreclosure Options",
                "points": ["Capital city resources", "Growing market", "Multiple solutions"],
                "dialogue": "If you're facing foreclosure in Sacramento, California's capital city offers resources and a growing market that can help you find a solution."
            },
            {
                "title": "Sacramento Market Trends",
                "points": ["Bay Area migration", "Rising values", "Strong buyer demand"],
                "dialogue": "Sacramento has seen incredible growth as Bay Area residents move east. Rising property values and strong buyer demand mean you may have more equity than you realize."
            },
            {
                "title": "Your Sacramento Options",
                "points": ["Loan modification", "Sell for cash", "Short sale if needed"],
                "dialogue": "Sacramento homeowners can pursue loan modification, sell for cash to keep equity, or arrange a short sale if underwater. Each situation is different, and we'll help you find the right path."
            },
            {
                "title": "Sacramento Experts",
                "points": ["Local knowledge", "Free consultation", "Fast action"],
                "dialogue": "My Foreclosure Solution helps Sacramento homeowners stop foreclosure fast. We offer free consultations and take fast action. Don't wait until it's too late. Call us today."
            }
        ]
    },
    "riverside-foreclosure": {
        "title": "Stop Foreclosure in Riverside",
        "sections": [
            {
                "title": "Riverside County Help",
                "points": ["Inland Empire solutions", "Affordable options", "We can help"],
                "dialogue": "Facing foreclosure in Riverside County? The Inland Empire has seen its share of foreclosures, but that means we have experience helping homeowners like you."
            },
            {
                "title": "Riverside Market Reality",
                "points": ["Growing population", "Improving values", "Buyer demand increasing"],
                "dialogue": "Riverside's growing population and improving home values mean there's demand for your property. Even in foreclosure, you may have options to keep equity or minimize damage."
            },
            {
                "title": "IE Foreclosure Solutions",
                "points": ["Sell fast for cash", "Avoid auction", "Protect your credit"],
                "dialogue": "We help Inland Empire homeowners sell fast for cash, avoid auction, and protect their credit. Whether you're in Riverside, Corona, or Moreno Valley, we can help."
            },
            {
                "title": "Get Riverside Help Now",
                "points": ["Free consultation", "No obligation", "Local expertise"],
                "dialogue": "Get your free consultation today. At My Foreclosure Solution, we have local expertise throughout Riverside County. Call us now and let's discuss your options."
            }
        ]
    },
    "orange-county-foreclosure": {
        "title": "Stop Foreclosure in Orange County",
        "sections": [
            {
                "title": "OC Foreclosure Solutions",
                "points": ["High-value market", "Significant equity possible", "Premium solutions"],
                "dialogue": "Facing foreclosure in Orange County? OC's high-value real estate market means you likely have significant equity worth protecting."
            },
            {
                "title": "Orange County Advantage",
                "points": ["Premium property values", "Strong buyer demand", "Quick sales possible"],
                "dialogue": "Orange County properties command premium prices. Whether you're in Irvine, Anaheim, or Newport Beach, strong buyer demand means quick sales are possible."
            },
            {
                "title": "Protect Your OC Equity",
                "points": ["Don't lose to auction", "Sell on your terms", "Keep your profit"],
                "dialogue": "Don't lose your equity to a foreclosure auction. Sell on your terms, keep your profit, and walk away with money for your fresh start."
            },
            {
                "title": "OC Experts Ready",
                "points": ["Free consultation", "We know OC market", "Call now"],
                "dialogue": "My Foreclosure Solution knows the Orange County market. We offer free consultations and fast solutions. Call us today and protect your equity."
            }
        ]
    }
}

# ============================================================
# DEEP DIVE / EDUCATIONAL VIDEOS
# ============================================================

EDUCATION_SCRIPTS = {
    "notice-of-default-explained": {
        "title": "Notice of Default Explained",
        "sections": [
            {
                "title": "What is a Notice of Default",
                "points": ["Official foreclosure document", "Filed with county", "Public record"],
                "dialogue": "What is a Notice of Default? It's an official document your lender files with the county recorder to start the foreclosure process. Once filed, it becomes public record."
            },
            {
                "title": "When is NOD Filed",
                "points": ["After 120 days delinquent", "Federal law requirement", "Lender must wait"],
                "dialogue": "Federal law requires lenders to wait at least 120 days after your first missed payment before filing a Notice of Default. This gives you time to work out solutions."
            },
            {
                "title": "What Happens After NOD",
                "points": ["90-day reinstatement period", "Can still save your home", "Clock is ticking"],
                "dialogue": "After the Notice of Default is filed, you have a 90-day reinstatement period. During this time, you can catch up on payments, sell your home, or negotiate with your lender."
            },
            {
                "title": "If You Received an NOD",
                "points": ["Don't panic", "Act immediately", "Get professional help"],
                "dialogue": "If you received a Notice of Default, don't panic, but do act immediately. Contact My Foreclosure Solution for a free consultation. We'll explain your options and help you take action."
            }
        ]
    },
    "short-sale-complete-guide": {
        "title": "Short Sale Complete Guide",
        "sections": [
            {
                "title": "What is a Short Sale",
                "points": ["Sell for less than owed", "Lender approves", "Avoid foreclosure"],
                "dialogue": "A short sale is when you sell your home for less than what you owe on the mortgage, with your lender's approval. It's a way to avoid foreclosure when you're underwater on your loan."
            },
            {
                "title": "Who Qualifies",
                "points": ["Financial hardship required", "Home worth less than owed", "Must be unable to pay"],
                "dialogue": "To qualify, you typically need to show financial hardship, your home must be worth less than you owe, and you must be unable to continue making payments."
            },
            {
                "title": "The Short Sale Process",
                "points": ["Find a buyer", "Submit to lender", "Lender reviews and approves"],
                "dialogue": "The process involves finding a buyer, submitting the offer to your lender, and waiting for lender approval. This can take 2 to 4 months, so patience is required."
            },
            {
                "title": "Short Sale vs Foreclosure",
                "points": ["Less credit damage", "May forgive remaining debt", "More control"],
                "dialogue": "A short sale is better than foreclosure. It does less damage to your credit, the lender may forgive the remaining debt, and you have more control over the process."
            },
            {
                "title": "Get Short Sale Help",
                "points": ["We handle everything", "Free consultation", "Lender negotiation"],
                "dialogue": "Short sales are complex. At My Foreclosure Solution, we handle everything including lender negotiation. Call for a free consultation to see if a short sale is right for you."
            }
        ]
    },
    "bankruptcy-and-foreclosure": {
        "title": "Bankruptcy and Foreclosure",
        "sections": [
            {
                "title": "Can Bankruptcy Stop Foreclosure",
                "points": ["Yes - automatic stay", "Stops all collection", "Immediate relief"],
                "dialogue": "Can bankruptcy stop foreclosure? Yes. Filing bankruptcy triggers an automatic stay that immediately stops foreclosure and all other collection actions."
            },
            {
                "title": "Chapter 7 vs Chapter 13",
                "points": ["Chapter 7 - temporary stop", "Chapter 13 - repayment plan", "Different outcomes"],
                "dialogue": "Chapter 7 bankruptcy temporarily stops foreclosure but may not save your home long-term. Chapter 13 lets you create a repayment plan to catch up on missed payments over 3 to 5 years."
            },
            {
                "title": "Bankruptcy Consequences",
                "points": ["Stays on credit 7-10 years", "Affects future borrowing", "Serious decision"],
                "dialogue": "Bankruptcy has serious consequences. It stays on your credit for 7 to 10 years and affects future borrowing. It should be a last resort, not a first choice."
            },
            {
                "title": "Explore All Options First",
                "points": ["Bankruptcy isn't only option", "Selling may be better", "Get professional advice"],
                "dialogue": "Before filing bankruptcy, explore all your options. Selling your home, loan modification, or short sale may be better choices. Contact My Foreclosure Solution for a free consultation to understand all your options."
            }
        ]
    }
}

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 Generating Additional Videos")
    print("=" * 60)

    all_scripts = {}
    all_scripts.update(FAQ_SCRIPTS)
    all_scripts.update(CITY_SCRIPTS)
    all_scripts.update(EDUCATION_SCRIPTS)

    for key, script in all_scripts.items():
        video_path = create_video(script, key)
        if video_path:
            vert_path = f"{OUTPUT_DIR}/{key}-VERTICAL.mp4"
            create_vertical(video_path, vert_path)

    print("\n" + "=" * 60)
    print("✅ All additional videos complete!")
    print(f"📁 {OUTPUT_DIR}")
    print("=" * 60)
