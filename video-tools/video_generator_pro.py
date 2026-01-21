#!/usr/bin/env python3
"""
Professional Video Generator with Voice, Music & End Screen
Pure FFmpeg approach - no ImageMagick needed
"""
import subprocess
import os
import tempfile

# Configuration
OUTPUT_DIR = "/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/test-outputs"
ASSETS_DIR = "/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/assets"
VOICE = "en-US-AndrewNeural"
VOICE_RATE = "-5%"

# Brand colors (hex without #)
BRAND_ORANGE = "FF6B35"
BRAND_DARK = "1a1a2e"

# Video settings
WIDTH = 1920
HEIGHT = 1080
FPS = 30

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

def generate_voice(text, output_path):
    """Generate voice using Edge TTS"""
    cmd = ["edge-tts", "--voice", VOICE, "--rate", VOICE_RATE, "--text", text, "--write-media", output_path]
    subprocess.run(cmd, capture_output=True, text=True)
    return os.path.exists(output_path)

def get_duration(path):
    """Get media duration"""
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 5.0

def create_section_video(title, points, dialogue, section_num, total, temp_dir):
    """Create a section video with text overlay"""
    audio_path = f"{temp_dir}/s{section_num}.mp3"
    video_path = f"{temp_dir}/s{section_num}.mp4"

    if not generate_voice(dialogue, audio_path):
        return None

    duration = get_duration(audio_path)

    # Build points text
    points_text = ""
    if points:
        for i, p in enumerate(points[:4]):
            if len(p) > 50:
                p = p[:47] + "..."
            points_text += f"• {p}\\n"

    # Clean title for ffmpeg
    title_clean = title.replace("'", "").replace(":", " -")
    points_clean = points_text.replace("'", "")

    # Progress bar position
    progress = section_num / total
    bar_width = int(1720 * progress)

    # Build filter with drawtext
    filter_parts = [
        # Dark gradient background
        f"color=c=0x{BRAND_DARK}:s={WIDTH}x{HEIGHT}:d={duration}",
        # Progress bar background
        f"drawbox=x=100:y={HEIGHT-60}:w=1720:h=20:color=0xffffff@0.2:t=fill",
        # Progress bar fill
        f"drawbox=x=100:y={HEIGHT-60}:w={bar_width}:h=20:color=0x{BRAND_ORANGE}:t=fill",
        # Section badge
        f"drawbox=x=80:y=80:w=100:h=60:color=0x{BRAND_ORANGE}:t=fill",
        f"drawtext=text='{section_num}/{total}':fontsize=30:fontcolor=white:x=95:y=95",
        # Title
        f"drawtext=text='{title_clean}':fontsize=56:fontcolor=white:x=(w-text_w)/2:y=180:font=Helvetica",
    ]

    # Add points if present
    if points_clean:
        filter_parts.append(
            f"drawtext=text='{points_clean}':fontsize=38:fontcolor=0xdddddd:x=150:y=320:line_spacing=20"
        )

    filter_str = ",".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", filter_str,
        "-i", audio_path,
        "-c:v", "libx264", "-c:a", "aac",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        video_path
    ]
    subprocess.run(cmd, capture_output=True)
    return video_path if os.path.exists(video_path) else None

def create_title_video(title, temp_dir):
    """Create title card video"""
    audio_path = f"{temp_dir}/title.mp3"
    video_path = f"{temp_dir}/title.mp4"

    intro = f"{title}. Let's dive in."
    generate_voice(intro, audio_path)
    duration = max(get_duration(audio_path), 4)

    title_clean = title.replace("'", "").replace(":", " -")
    subtitle = "Expert Tips from MyForeclosureSolution.com"

    filter_str = ",".join([
        f"color=c=0x{BRAND_DARK}:s={WIDTH}x{HEIGHT}:d={duration}",
        f"drawtext=text='{title_clean}':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-40",
        f"drawtext=text='{subtitle}':fontsize=32:fontcolor=0x{BRAND_ORANGE}:x=(w-text_w)/2:y=(h-text_h)/2+60",
    ])

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", filter_str,
        "-i", audio_path,
        "-c:v", "libx264", "-c:a", "aac",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        video_path
    ]
    subprocess.run(cmd, capture_output=True)
    return video_path if os.path.exists(video_path) else None

def create_end_video(temp_dir):
    """Create end screen with CTA"""
    audio_path = f"{temp_dir}/end.mp3"
    video_path = f"{temp_dir}/end.mp4"

    outro = "Thanks for watching! Visit MyForeclosureSolution.com for your free consultation. Subscribe for more tips!"
    generate_voice(outro, audio_path)
    duration = get_duration(audio_path) + 2

    filter_str = ",".join([
        f"color=c=0x{BRAND_DARK}:s={WIDTH}x{HEIGHT}:d={duration}",
        # CTA button
        f"drawbox=x={WIDTH//2-350}:y={HEIGHT//2-50}:w=700:h=100:color=0x{BRAND_ORANGE}:t=fill",
        f"drawtext=text='Get Your FREE Consultation':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
        # Website
        f"drawtext=text='MyForeclosureSolution.com':fontsize=48:fontcolor=white:x=(w-text_w)/2:y={HEIGHT//2+100}",
        # Phone
        f"drawtext=text='(949) 565-5285':fontsize=32:fontcolor=0xaaaaaa:x=(w-text_w)/2:y={HEIGHT//2+170}",
        # Subscribe
        f"drawtext=text='SUBSCRIBE for more foreclosure tips':fontsize=28:fontcolor=0x{BRAND_ORANGE}:x=(w-text_w)/2:y={HEIGHT-120}",
    ])

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", filter_str,
        "-i", audio_path,
        "-c:v", "libx264", "-c:a", "aac",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        video_path
    ]
    subprocess.run(cmd, capture_output=True)
    return video_path if os.path.exists(video_path) else None

def create_ambient_music(duration, output_path):
    """Create subtle ambient background"""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=180:duration={duration}",
        "-af", "volume=0.015,lowpass=f=300,tremolo=f=0.1:d=0.3",
        "-c:a", "libmp3lame",
        output_path
    ]
    subprocess.run(cmd, capture_output=True)

def add_music_to_video(video_path, output_path):
    """Add background music to final video"""
    duration = get_duration(video_path)
    music_path = f"{os.path.dirname(video_path)}/music.mp3"
    create_ambient_music(duration + 5, music_path)

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", music_path,
        "-filter_complex", f"[1:a]volume=0.08,afade=t=out:st={duration-3}:d=3[m];[0:a][m]amix=inputs=2:duration=first[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac",
        output_path
    ]
    subprocess.run(cmd, capture_output=True)

def create_vertical(input_path, output_path):
    """Create 9:16 vertical version (60 sec max for Shorts)"""
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
        "-c:a", "copy",
        "-t", "59",
        output_path
    ]
    subprocess.run(cmd, capture_output=True)

def create_video(script, output_name):
    """Create complete video"""
    ensure_dirs()

    title = script["title"]
    sections = script["sections"]

    print(f"\n🎬 Creating: {title}")

    with tempfile.TemporaryDirectory() as temp_dir:
        segments = []

        # Title card
        print("  → Title card...")
        title_vid = create_title_video(title, temp_dir)
        if title_vid:
            segments.append(title_vid)
            print(f"     ✓ {get_duration(title_vid):.1f}s")

        # Sections
        total = len([s for s in sections if s.get("dialogue")])
        num = 0
        for section in sections:
            if not section.get("dialogue"):
                continue
            num += 1
            print(f"  → Section {num}/{total}: {section['title'][:35]}...")
            seg = create_section_video(
                section["title"],
                section.get("points", []),
                section["dialogue"],
                num, total, temp_dir
            )
            if seg:
                segments.append(seg)
                print(f"     ✓ {get_duration(seg):.1f}s")

        # End screen
        print("  → End screen...")
        end_vid = create_end_video(temp_dir)
        if end_vid:
            segments.append(end_vid)
            print(f"     ✓ {get_duration(end_vid):.1f}s")

        # Concatenate
        print("  → Combining...")
        concat_file = f"{temp_dir}/list.txt"
        with open(concat_file, "w") as f:
            for seg in segments:
                f.write(f"file '{seg}'\n")

        raw_path = f"{temp_dir}/raw.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c:v", "libx264", "-c:a", "aac",
            raw_path
        ]
        subprocess.run(cmd, capture_output=True)

        # Add watermark text
        print("  → Adding watermark...")
        watermark_path = f"{temp_dir}/watermark.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-i", raw_path,
            "-vf", f"drawtext=text='MyForeclosureSolution.com':fontsize=24:fontcolor=white@0.6:x=w-text_w-30:y=30",
            "-c:a", "copy",
            watermark_path
        ]
        subprocess.run(cmd, capture_output=True)

        # Add music
        print("  → Adding music...")
        final_path = f"{OUTPUT_DIR}/{output_name}.mp4"
        add_music_to_video(watermark_path, final_path)

        if os.path.exists(final_path):
            duration = get_duration(final_path)
            size = os.path.getsize(final_path) / (1024*1024)
            print(f"\n✅ {output_name}.mp4 ({duration/60:.1f} min, {size:.1f} MB)")

            # Create vertical version
            print("  → Creating vertical version...")
            vert_path = f"{OUTPUT_DIR}/{output_name}-VERTICAL.mp4"
            create_vertical(final_path, vert_path)
            if os.path.exists(vert_path):
                print(f"   📱 {output_name}-VERTICAL.mp4 (59s)")

            return final_path
        return None

# ============================================================
# VIDEO SCRIPTS
# ============================================================

SCRIPTS = {
    "foreclosure-options": {
        "title": "How to Stop Foreclosure in California",
        "sections": [
            {
                "title": "The 4 Main Options",
                "points": ["Loan Modification", "Forbearance", "Short Sale", "Sell Your Home Fast"],
                "dialogue": "If you're facing foreclosure in California, you have four main options. Let me walk you through each one."
            },
            {
                "title": "Option 1 - Loan Modification",
                "points": ["Lower monthly payments", "Extend loan term", "Reduce interest rate"],
                "dialogue": "Option one is a loan modification. Work with your lender to change your mortgage terms. They might lower your interest rate or extend your loan to make payments affordable."
            },
            {
                "title": "Option 2 - Forbearance",
                "points": ["Temporary payment pause", "Good for short-term hardship", "Must repay later"],
                "dialogue": "Option two is forbearance. This is a temporary pause in payments. Great for short-term hardship, but you'll need to repay the missed amount later."
            },
            {
                "title": "Option 3 - Short Sale",
                "points": ["Sell for less than owed", "Lender approves sale", "Better than foreclosure"],
                "dialogue": "Option three is a short sale. Sell your home for less than you owe with lender approval. It's much better for your credit than a foreclosure."
            },
            {
                "title": "Option 4 - Sell Fast for Cash",
                "points": ["Cash offer in 24 hours", "Close in 7 days", "No repairs needed"],
                "dialogue": "Option four is selling fast to a cash buyer. Get an offer in 24 hours, close in as little as 7 days, and walk away with money. No repairs, no fees."
            },
            {
                "title": "California Timeline",
                "points": ["120 days before NOD", "90 days to reinstate", "About 200 days total"],
                "dialogue": "California's foreclosure process takes about 200 days. That gives you time to act, but don't wait. The sooner you act, the more options you have."
            },
            {
                "title": "Get Free Help Today",
                "points": ["Free consultation", "No obligation", "Call now"],
                "dialogue": "At My Foreclosure Solution, we offer free consultations. We've helped hundreds of California homeowners. Call us today."
            }
        ]
    },
    "warning-signs": {
        "title": "5 Warning Signs of Foreclosure",
        "sections": [
            {
                "title": "Know the Warning Signs",
                "points": ["Early detection is key", "More time equals more options"],
                "dialogue": "Foreclosure doesn't happen overnight. Knowing the warning signs early gives you more time and more options."
            },
            {
                "title": "Sign 1 - Missed Payments",
                "points": ["One missed is a warning", "Three triggers foreclosure"],
                "dialogue": "Warning sign one: missed payments. Even one should be a wake-up call. After three, the foreclosure process can begin."
            },
            {
                "title": "Sign 2 - Notice of Default",
                "points": ["Official foreclosure document", "Starts 90-day clock"],
                "dialogue": "Warning sign two: receiving a Notice of Default. This official document starts the foreclosure clock. You have 90 days to act."
            },
            {
                "title": "Sign 3 - Lender Calls",
                "points": ["Letters about payments", "Offers to discuss options"],
                "dialogue": "Warning sign three: increased lender contact. If you're getting letters and calls about missed payments, don't ignore them."
            },
            {
                "title": "Sign 4 - Financial Stress",
                "points": ["Using credit for bills", "Borrowing from retirement"],
                "dialogue": "Warning sign four: overall financial stress. Using credit cards for basic bills? Borrowing from retirement? Foreclosure might be closer than you think."
            },
            {
                "title": "Sign 5 - Life Changes",
                "points": ["Job loss", "Divorce", "Medical emergency"],
                "dialogue": "Warning sign five: major life changes. Job loss, divorce, or serious illness can trigger foreclosure. But help is available."
            },
            {
                "title": "Take Action Now",
                "points": ["Don't wait", "Free help available"],
                "dialogue": "If you recognize these signs, take action now. At My Foreclosure Solution, we offer free consultations. Call us today."
            }
        ]
    },
    "sell-during-foreclosure": {
        "title": "Can You Sell During Foreclosure",
        "sections": [
            {
                "title": "Yes You Can Sell",
                "points": ["Legal right to sell", "Up until auction day"],
                "dialogue": "Can you sell your house during foreclosure? Yes, absolutely. You have the legal right to sell until auction day."
            },
            {
                "title": "Two Scenarios",
                "points": ["With equity - keep profits", "Underwater - need short sale"],
                "dialogue": "There are two scenarios. If you have equity, sell and keep the difference. If underwater, you'll need lender approval for a short sale."
            },
            {
                "title": "Selling With Equity",
                "points": ["Cash buyers are fastest", "Close in days not months"],
                "dialogue": "With equity, cash buyers are your fastest option. They can close in days, not months. Pay off the mortgage and keep the rest."
            },
            {
                "title": "Short Sale Explained",
                "points": ["Lender accepts less", "Takes 2-4 months", "Better than foreclosure"],
                "dialogue": "A short sale means your lender accepts less than owed. It takes longer but is much better for your credit than foreclosure."
            },
            {
                "title": "Benefits of Selling",
                "points": ["Avoid foreclosure on credit", "May get cash", "Stay in control"],
                "dialogue": "Selling beats foreclosure. Avoid damage to your credit, possibly walk away with cash, and stay in control of the process."
            },
            {
                "title": "Cash Buyer Advantage",
                "points": ["7-14 day closing", "No repairs", "Guaranteed"],
                "dialogue": "Cash buyers offer speed and certainty. Close in 7 to 14 days, no repairs needed, and a guaranteed closing."
            },
            {
                "title": "Contact Us Today",
                "points": ["Free home valuation", "No obligation"],
                "dialogue": "At My Foreclosure Solution, we provide free home valuations. Contact us today for a no-obligation consultation."
            }
        ]
    },
    "california-timeline": {
        "title": "California Foreclosure Timeline",
        "sections": [
            {
                "title": "Understanding the Process",
                "points": ["Non-judicial process", "Takes 180-200 days"],
                "dialogue": "California uses a non-judicial foreclosure process. The entire timeline is typically 180 to 200 days from first missed payment."
            },
            {
                "title": "Days 1-30 - First Miss",
                "points": ["Grace period applies", "Lender contacts you"],
                "dialogue": "After your first missed payment, there's usually a grace period. Your lender will contact you. One miss won't trigger foreclosure."
            },
            {
                "title": "Days 31-120 - Delinquency",
                "points": ["Multiple missed payments", "Lender must offer options"],
                "dialogue": "Between days 31 and 120, you're delinquent. Your lender must offer loss mitigation options. Use this time wisely."
            },
            {
                "title": "Day 120 - Notice of Default",
                "points": ["Official start", "90 days to reinstate"],
                "dialogue": "After 120 days, the lender files a Notice of Default. You now have 90 days to catch up on all missed payments."
            },
            {
                "title": "Day 210 - Notice of Sale",
                "points": ["Auction date set", "21-day minimum notice"],
                "dialogue": "If you don't reinstate, a Notice of Trustee Sale is filed. Your auction date is set at least 21 days out."
            },
            {
                "title": "Auction Day",
                "points": ["Public sale", "No redemption after"],
                "dialogue": "On auction day, your home is sold to the highest bidder. In California, there's no redemption period after."
            },
            {
                "title": "Act Early",
                "points": ["Earlier equals more options", "Free help available"],
                "dialogue": "The earlier you act, the more options you have. At My Foreclosure Solution, we help at every stage. Call for your free consultation."
            }
        ]
    }
}

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 Professional Video Generator")
    print("=" * 60)

    for key, script in SCRIPTS.items():
        create_video(script, key)

    print("\n" + "=" * 60)
    print("✅ All videos complete!")
    print(f"📁 {OUTPUT_DIR}")
    print("=" * 60)
