#!/usr/bin/env python3
"""
ENGAGING Video Generator - Reliable + High Quality
Dynamic visuals, better voice, compelling scripts
"""
import subprocess
import os
import tempfile

OUTPUT_DIR = "/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/final-videos"
VOICE = "en-US-GuyNeural"  # Energetic male voice
VOICE_RATE = "+10%"  # Faster, more dynamic

WIDTH = 1920
HEIGHT = 1080

# Vibrant colors
ORANGE = "FF6B35"
BLUE = "1E3A5F"
DARK = "0D1B2A"
TEAL = "00D4AA"

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def voice(text, path):
    cmd = ["edge-tts", "--voice", VOICE, "--rate", VOICE_RATE, "--text", text, "--write-media", path]
    subprocess.run(cmd, capture_output=True)
    return os.path.exists(path)

def duration(path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except: return 5.0

def make_segment(title, body, num, total, temp_dir, seg_type="info"):
    """Create one video segment"""
    audio = f"{temp_dir}/seg{num}.mp3"
    video = f"{temp_dir}/seg{num}.mp4"

    if not voice(body, audio):
        return None

    dur = duration(audio) + 0.3
    title = title.replace("'", "").replace(":", " -")

    # Color based on type
    if seg_type == "hook":
        bg, accent = DARK, ORANGE
    elif seg_type == "warning":
        bg, accent = "8B0000", "FFCC00"  # Red + gold
    elif seg_type == "tip":
        bg, accent = BLUE, TEAL
    elif seg_type == "cta":
        bg, accent = ORANGE, "FFFFFF"
    else:
        bg, accent = DARK, TEAL

    # Progress bar width
    prog_w = int(1720 * (num / total)) if total > 0 else 0

    # Build ffmpeg filter
    vf = (
        f"color=0x{bg}:s={WIDTH}x{HEIGHT}:d={dur},"
        # Accent stripe on left
        f"drawbox=x=0:y=0:w=12:h=ih:c=0x{accent}:t=fill,"
        # Section number
        f"drawtext=text='{num}':fontsize=140:fontcolor=0x{accent}:x=60:y=50,"
        f"drawtext=text='of {total}':fontsize=28:fontcolor=white@0.5:x=75:y=195,"
        # Title
        f"drawtext=text='{title.upper()}':fontsize=52:fontcolor=white:x=200:y=100,"
        # Progress bar
        f"drawbox=x=100:y=ih-40:w=1720:h=8:c=white@0.2:t=fill,"
        f"drawbox=x=100:y=ih-40:w={prog_w}:h=8:c=0x{accent}:t=fill,"
        # Website watermark
        f"drawtext=text='MyForeclosureSolution.com':fontsize=24:fontcolor=white@0.5:x=w-text_w-30:y=30"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=0x{bg}:s={WIDTH}x{HEIGHT}:d={dur}",
        "-i", audio,
        "-vf", vf,
        "-c:v", "libx264", "-c:a", "aac", "-shortest",
        "-pix_fmt", "yuv420p",
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def make_hook(hook_text, temp_dir):
    """Create attention-grabbing hook"""
    audio = f"{temp_dir}/hook.mp3"
    video = f"{temp_dir}/hook.mp4"

    voice(hook_text, audio)
    dur = duration(audio) + 0.5

    hook_clean = hook_text.replace("'", "").upper()

    vf = (
        f"color=0x{DARK}:s={WIDTH}x{HEIGHT}:d={dur},"
        f"drawbox=x=iw/2-500:y=ih/2-80:w=1000:h=160:c=0x{ORANGE}:t=fill,"
        f"drawtext=text='{hook_clean}':fontsize=56:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=0x{DARK}:s={WIDTH}x{HEIGHT}:d={dur}",
        "-i", audio,
        "-vf", vf,
        "-c:v", "libx264", "-c:a", "aac", "-shortest",
        "-pix_fmt", "yuv420p",
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def make_title(title, temp_dir):
    """Create title card"""
    audio = f"{temp_dir}/title.mp3"
    video = f"{temp_dir}/title.mp4"

    voice(title, audio)
    dur = duration(audio) + 1

    title_clean = title.replace("'", "").upper()

    vf = (
        f"color=0x{BLUE}:s={WIDTH}x{HEIGHT}:d={dur},"
        f"drawtext=text='{title_clean}':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-40,"
        f"drawtext=text='MyForeclosureSolution.com':fontsize=36:fontcolor=0x{TEAL}:x=(w-text_w)/2:y=(h-text_h)/2+60,"
        f"drawbox=x=iw/2-300:y=ih/2+120:w=600:h=4:c=0x{ORANGE}:t=fill"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=0x{BLUE}:s={WIDTH}x{HEIGHT}:d={dur}",
        "-i", audio,
        "-vf", vf,
        "-c:v", "libx264", "-c:a", "aac", "-shortest",
        "-pix_fmt", "yuv420p",
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def make_cta(temp_dir):
    """Create call to action"""
    audio = f"{temp_dir}/cta.mp3"
    video = f"{temp_dir}/cta.mp4"

    cta = "Call us right now for your free consultation. We have helped hundreds of California homeowners save their homes. That call could change everything."
    voice(cta, audio)
    dur = duration(audio) + 2

    vf = (
        f"color=0x{ORANGE}:s={WIDTH}x{HEIGHT}:d={dur},"
        f"drawbox=x=0:y=0:w=iw:h=ih:c=0x{DARK}@0.85:t=fill,"
        f"drawbox=x=iw/2-350:y=ih/2-70:w=700:h=140:c=0x{ORANGE}:t=fill,"
        f"drawtext=text='CALL NOW':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-30,"
        f"drawtext=text='(949) 565-5285':fontsize=56:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2+100,"
        f"drawtext=text='MyForeclosureSolution.com':fontsize=40:fontcolor=0x{TEAL}:x=(w-text_w)/2:y=(h-text_h)/2+200,"
        f"drawtext=text='FREE CONSULTATION':fontsize=28:fontcolor=white@0.7:x=(w-text_w)/2:y=ih-80"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=0x{ORANGE}:s={WIDTH}x{HEIGHT}:d={dur}",
        "-i", audio,
        "-vf", vf,
        "-c:v", "libx264", "-c:a", "aac", "-shortest",
        "-pix_fmt", "yuv420p",
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def make_end(temp_dir):
    """Create end screen"""
    video = f"{temp_dir}/end.mp4"
    dur = 5

    vf = (
        f"color=0x{DARK}:s={WIDTH}x{HEIGHT}:d={dur},"
        f"drawbox=x=iw/2-120:y=ih/2-120:w=240:h=240:c=0xFF0000:t=fill,"
        f"drawtext=text='SUBSCRIBE':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-10,"
        f"drawtext=text='for more tips':fontsize=28:fontcolor=white@0.7:x=(w-text_w)/2:y=(h-text_h)/2+35,"
        f"drawtext=text='Like and Share if this helped!':fontsize=32:fontcolor=0x{TEAL}:x=(w-text_w)/2:y=ih-120"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=0x{DARK}:s={WIDTH}x{HEIGHT}:d={dur}",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-vf", vf,
        "-c:v", "libx264", "-c:a", "aac", "-t", str(dur),
        "-pix_fmt", "yuv420p",
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def add_music(video_path, output_path):
    """Add subtle background music"""
    dur = duration(video_path)

    # Create ambient music
    music = f"{os.path.dirname(video_path)}/music.mp3"
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"sine=f=120:d={dur+5}",
        "-af", f"volume=0.015,lowpass=f=300,afade=t=out:st={dur-3}:d=3",
        "-c:a", "libmp3lame", music
    ]
    subprocess.run(cmd, capture_output=True)

    # Mix
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", music,
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:weights=1 0.2[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac",
        output_path
    ]
    subprocess.run(cmd, capture_output=True)
    return os.path.exists(output_path)

def create_video(script, output_name):
    """Create complete engaging video"""
    ensure_dirs()

    title = script["title"]
    hook = script.get("hook", "Watch this before its too late")
    sections = script["sections"]

    print(f"\n🎬 {title}")

    with tempfile.TemporaryDirectory() as temp:
        parts = []

        # Hook
        print("  → Hook...")
        h = make_hook(hook, temp)
        if h:
            parts.append(h)
            print(f"     ✓ {duration(h):.1f}s")

        # Title
        print("  → Title...")
        t = make_title(title, temp)
        if t:
            parts.append(t)
            print(f"     ✓ {duration(t):.1f}s")

        # Sections
        total = len(sections)
        for i, sec in enumerate(sections, 1):
            print(f"  → {i}/{total}: {sec['title'][:30]}...")
            s = make_segment(
                sec["title"],
                sec["dialogue"],
                i, total, temp,
                sec.get("type", "info")
            )
            if s:
                parts.append(s)
                print(f"     ✓ {duration(s):.1f}s")

        # CTA
        print("  → CTA...")
        c = make_cta(temp)
        if c:
            parts.append(c)
            print(f"     ✓ {duration(c):.1f}s")

        # End
        print("  → End screen...")
        e = make_end(temp)
        if e:
            parts.append(e)
            print(f"     ✓ {duration(e):.1f}s")

        # Concat
        print("  → Combining...")
        concat_file = f"{temp}/list.txt"
        with open(concat_file, "w") as f:
            for p in parts:
                f.write(f"file '{p}'\n")

        raw = f"{temp}/raw.mp4"
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c:v", "libx264", "-c:a", "aac",
            raw
        ]
        subprocess.run(cmd, capture_output=True)

        # Add music
        print("  → Adding music...")
        final = f"{OUTPUT_DIR}/{output_name}.mp4"
        add_music(raw, final)

        if os.path.exists(final):
            d = duration(final)
            s = os.path.getsize(final) / (1024*1024)
            print(f"\n✅ {output_name}.mp4 ({d/60:.1f} min, {s:.1f} MB)")
            return final

    return None

# ============================================================
# ENGAGING SCRIPTS
# ============================================================

SCRIPTS = {
    "stop-foreclosure-fast": {
        "title": "How to Stop Foreclosure FAST",
        "hook": "STOP! What Im about to tell you could save your home",
        "sections": [
            {
                "title": "Your Bank Has a Secret",
                "dialogue": "Heres what your bank will never tell you. They dont actually want to foreclose. It costs them tens of thousands of dollars. They would rather work something out. And thats your leverage.",
                "type": "hook"
            },
            {
                "title": "Option 1 - Loan Modification",
                "dialogue": "First option - loan modification. Your bank rewrites your loan to make it affordable. Lower rate. Longer term. Lower payment. Banks approve these more than you think. You just need to know how to ask.",
                "type": "tip"
            },
            {
                "title": "Option 2 - Forbearance",
                "dialogue": "Second option - forbearance. Lost your job? Medical emergency? This pauses your payments while you recover. The key is acting fast.",
                "type": "tip"
            },
            {
                "title": "Option 3 - Sell Fast",
                "dialogue": "Third option - and most people miss this - sell your home fast. Even in foreclosure, you probably have equity. Sell to a cash buyer, pay off the mortgage, walk away with money. Way better than losing everything at auction.",
                "type": "tip"
            },
            {
                "title": "The Big Mistake",
                "dialogue": "The biggest mistake? Ignoring it. People bury their head in the sand. They dont open the mail. They dont answer the phone. And by the time they act, they have no options left. Dont be that person.",
                "type": "warning"
            },
            {
                "title": "Take Action Now",
                "dialogue": "Heres what to do right now. Call us for a free consultation. Well look at your specific situation and tell you exactly what options you have. No pressure. No games. Just real answers.",
                "type": "cta"
            }
        ]
    },
    "5-mistakes": {
        "title": "5 Mistakes That Cost You Your Home",
        "hook": "Are you making these fatal foreclosure mistakes?",
        "sections": [
            {
                "title": "Mistake 1 - Ignoring It",
                "dialogue": "Mistake one - ignoring the problem. Those letters are scary, I get it. But every day you ignore them, you lose options. The foreclosure clock is ticking. Your silence only helps the bank.",
                "type": "warning"
            },
            {
                "title": "Mistake 2 - Closed Mail",
                "dialogue": "Mistake two - not opening your mail. Those certified letters have deadlines. Notice of Default. Notice of Sale. Miss a deadline, lose a right. Open every single letter.",
                "type": "warning"
            },
            {
                "title": "Mistake 3 - Waiting for Miracles",
                "dialogue": "Mistake three - waiting for a miracle. Hoping to win the lottery. Waiting for someone to rescue you. Hope is not a strategy. Only action works.",
                "type": "warning"
            },
            {
                "title": "Mistake 4 - Scammers",
                "dialogue": "Mistake four - falling for scammers. Con artists target people in foreclosure. Never pay huge upfront fees. Never sign over your deed. If it sounds too good to be true, run.",
                "type": "warning"
            },
            {
                "title": "Mistake 5 - Giving Up",
                "dialogue": "Mistake five - giving up too early. Ive seen people save their homes days before auction. Options exist until that gavel falls. Never assume its over.",
                "type": "warning"
            },
            {
                "title": "Theres Still Time",
                "dialogue": "If youre watching this, theres still time. You havent lost yet. Call us now for a free consultation. That call could save your home.",
                "type": "cta"
            }
        ]
    },
    "california-timeline": {
        "title": "California Foreclosure Timeline",
        "hook": "Know exactly how much time you have",
        "sections": [
            {
                "title": "The 200 Day Clock",
                "dialogue": "In California, foreclosure takes about 200 days from your first missed payment to the auction. Thats over 6 months. But that time goes fast if you dont use it.",
                "type": "info"
            },
            {
                "title": "Days 1 to 120",
                "dialogue": "Days 1 to 120 - you're delinquent but not yet in foreclosure. The bank must wait 120 days before filing anything. Use this time to negotiate.",
                "type": "info"
            },
            {
                "title": "Notice of Default",
                "dialogue": "After 120 days, the bank files a Notice of Default. This is the official start. You now have 90 days to catch up or find another solution.",
                "type": "warning"
            },
            {
                "title": "Notice of Sale",
                "dialogue": "If you dont fix it, they file Notice of Sale. Your auction date is set. At least 21 days notice. This is the final countdown.",
                "type": "warning"
            },
            {
                "title": "Auction Day",
                "dialogue": "Auction day - your home sells to the highest bidder. No redemption period in California. Once its sold, its gone. Dont let it get here.",
                "type": "warning"
            },
            {
                "title": "Act Now",
                "dialogue": "Wherever you are in this timeline, options exist. But they shrink every day. Call us now for a free consultation. Lets figure out your best move.",
                "type": "cta"
            }
        ]
    },
    "sell-during-foreclosure": {
        "title": "Sell Your House During Foreclosure",
        "hook": "You can still sell - and keep your equity",
        "sections": [
            {
                "title": "Yes You Can Sell",
                "dialogue": "Can you sell your house during foreclosure? Absolutely yes. You have the legal right to sell until the auction. Most people dont know this.",
                "type": "tip"
            },
            {
                "title": "Why Selling Wins",
                "dialogue": "Why is selling better than foreclosure? You keep your equity. You control the timeline. And your credit takes way less damage. Win win win.",
                "type": "tip"
            },
            {
                "title": "Cash Buyers Are Key",
                "dialogue": "The secret is cash buyers. We can close in 7 days. No banks, no delays. Traditional buyers take months - you dont have months.",
                "type": "tip"
            },
            {
                "title": "Short Sale Option",
                "dialogue": "What if you owe more than its worth? Thats a short sale. The bank accepts less than you owe. Takes longer but still better than foreclosure.",
                "type": "info"
            },
            {
                "title": "Dont Lose It At Auction",
                "dialogue": "Heres the nightmare scenario. Auction happens. Bank takes your house. Keeps all your equity. Youre left with nothing and wrecked credit. Dont let this happen.",
                "type": "warning"
            },
            {
                "title": "Get Your Cash Offer",
                "dialogue": "Call us today for a free cash offer on your home. No repairs. No fees. No obligations. Just a real number you can count on.",
                "type": "cta"
            }
        ]
    },
    "los-angeles": {
        "title": "Stop Foreclosure Los Angeles",
        "hook": "LA homeowners - you have more equity than you think",
        "sections": [
            {
                "title": "LA Market Advantage",
                "dialogue": "Los Angeles real estate is hot. Even in foreclosure, your property likely has serious equity. That money belongs to you - not the bank.",
                "type": "tip"
            },
            {
                "title": "High Demand Works For You",
                "dialogue": "Cash buyers are fighting over LA properties. That competition means better offers for you. We can close fast before your auction date.",
                "type": "tip"
            },
            {
                "title": "Every Neighborhood",
                "dialogue": "We buy houses everywhere in LA. The Valley. South LA. East LA. Westside. Doesnt matter the condition. We buy as-is.",
                "type": "info"
            },
            {
                "title": "LA Local Experts",
                "dialogue": "We know Los Angeles. We know the courts. We know the timeline. And we know how to move fast when you need it.",
                "type": "info"
            },
            {
                "title": "Call Us Today",
                "dialogue": "Los Angeles homeowners - dont lose your equity to auction. Call us now for a free consultation and cash offer. We can help.",
                "type": "cta"
            }
        ]
    },
    "san-diego": {
        "title": "Stop Foreclosure San Diego",
        "hook": "San Diego homeowners - save your home or your equity",
        "sections": [
            {
                "title": "San Diego Values Are High",
                "dialogue": "San Diego property values are among the highest in California. Your home has equity worth fighting for. Dont let the bank take it.",
                "type": "tip"
            },
            {
                "title": "Military Families Welcome",
                "dialogue": "We specialize in helping military families facing foreclosure. PCS orders. Deployment issues. We understand and we can help.",
                "type": "info"
            },
            {
                "title": "All San Diego County",
                "dialogue": "Chula Vista. Oceanside. Escondido. El Cajon. All of San Diego County. We buy houses everywhere.",
                "type": "info"
            },
            {
                "title": "Fast Cash Closings",
                "dialogue": "When you need to move fast, we deliver. Cash offers within 24 hours. Close in 7 days. No games.",
                "type": "tip"
            },
            {
                "title": "Free San Diego Consultation",
                "dialogue": "San Diego homeowners - call us today. Free consultation. Free cash offer. No obligation. Lets save your equity.",
                "type": "cta"
            }
        ]
    }
}

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 ENGAGING Video Generator")
    print("=" * 60)

    for key, script in SCRIPTS.items():
        create_video(script, key)

    print("\n" + "=" * 60)
    print("✅ All videos complete!")
    print(f"📁 {OUTPUT_DIR}")
    print("=" * 60)
