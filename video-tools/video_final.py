#!/usr/bin/env python3
"""
FINAL Video Generator - Working, Engaging, Professional
"""
import subprocess
import os
import tempfile

OUTPUT = "/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/final-videos"
VOICE = "en-US-GuyNeural"

# Colors
ORANGE = "FF6B35"
BLUE = "1E3A5F"
DARK = "0D1B2A"
TEAL = "00D4AA"
RED = "CC0000"

os.makedirs(OUTPUT, exist_ok=True)

def tts(text, path):
    subprocess.run(["edge-tts", "--voice", VOICE, "--rate", "+10%", "--text", text, "--write-media", path], capture_output=True)
    return os.path.exists(path)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except: return 5.0

def segment(text_top, text_main, dialogue, num, total, color, accent, temp):
    """Create one segment with ffmpeg"""
    audio = f"{temp}/s{num}.mp3"
    video = f"{temp}/s{num}.mp4"

    if not tts(dialogue, audio):
        return None

    d = dur(audio) + 0.3
    text_top = text_top.replace("'", "").replace(":", "")[:50]
    progress_w = int(1700 * (num / total)) if total > 0 else 100

    # Build filter
    filt = (
        f"[0:v]"
        f"drawbox=x=0:y=0:w=12:h=ih:c=0x{accent}:t=fill,"
        f"drawtext=text='{num}':fontsize=120:fontcolor=0x{accent}:x=50:y=40,"
        f"drawtext=text='of {total}':fontsize=24:fontcolor=white@0.5:x=65:y=165,"
        f"drawtext=text='{text_top.upper()}':fontsize=48:fontcolor=white:x=180:y=90,"
        f"drawbox=x=100:y=ih-35:w=1700:h=6:c=white@0.2:t=fill,"
        f"drawbox=x=100:y=ih-35:w={progress_w}:h=6:c=0x{accent}:t=fill,"
        f"drawtext=text='MyForeclosureSolution.com':fontsize=22:fontcolor=white@0.4:x=w-text_w-25:y=25"
        f"[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x{color}:s=1920x1080:d={d}",
        "-i", audio,
        "-filter_complex", filt,
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def hook(text, temp):
    audio = f"{temp}/hook.mp3"
    video = f"{temp}/hook.mp4"
    tts(text, audio)
    d = dur(audio) + 0.5
    text = text.replace("'", "")[:60].upper()

    filt = (
        f"[0:v]"
        f"drawbox=x=iw/2-450:y=ih/2-60:w=900:h=120:c=0x{ORANGE}:t=fill,"
        f"drawtext=text='{text}':fontsize=44:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2"
        f"[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x{DARK}:s=1920x1080:d={d}",
        "-i", audio,
        "-filter_complex", filt,
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def title_card(text, temp):
    audio = f"{temp}/title.mp3"
    video = f"{temp}/title.mp4"
    tts(text, audio)
    d = dur(audio) + 1
    text = text.replace("'", "")[:60].upper()

    filt = (
        f"[0:v]"
        f"drawtext=text='{text}':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-30,"
        f"drawtext=text='MyForeclosureSolution.com':fontsize=32:fontcolor=0x{TEAL}:x=(w-text_w)/2:y=(h-text_h)/2+50,"
        f"drawbox=x=iw/2-250:y=ih/2+100:w=500:h=4:c=0x{ORANGE}:t=fill"
        f"[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x{BLUE}:s=1920x1080:d={d}",
        "-i", audio,
        "-filter_complex", filt,
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def cta_card(temp):
    audio = f"{temp}/cta.mp3"
    video = f"{temp}/cta.mp4"
    tts("Call us right now for your free consultation. We help California homeowners every day. That call could change everything.", audio)
    d = dur(audio) + 2

    filt = (
        f"[0:v]"
        f"drawbox=x=0:y=0:w=iw:h=ih:c=0x{DARK}@0.85:t=fill,"
        f"drawbox=x=iw/2-300:y=ih/2-60:w=600:h=120:c=0x{ORANGE}:t=fill,"
        f"drawtext=text='CALL NOW':fontsize=56:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-20,"
        f"drawtext=text='(949) 565-5285':fontsize=52:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2+90,"
        f"drawtext=text='MyForeclosureSolution.com':fontsize=36:fontcolor=0x{TEAL}:x=(w-text_w)/2:y=(h-text_h)/2+180,"
        f"drawtext=text='FREE CONSULTATION - NO OBLIGATION':fontsize=24:fontcolor=white@0.6:x=(w-text_w)/2:y=ih-70"
        f"[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x{ORANGE}:s=1920x1080:d={d}",
        "-i", audio,
        "-filter_complex", filt,
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def end_screen(temp):
    video = f"{temp}/end.mp4"

    filt = (
        f"[0:v]"
        f"drawbox=x=iw/2-100:y=ih/2-100:w=200:h=200:c=0xFF0000:t=fill,"
        f"drawtext=text='SUBSCRIBE':fontsize=36:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-10,"
        f"drawtext=text='for tips':fontsize=24:fontcolor=white@0.7:x=(w-text_w)/2:y=(h-text_h)/2+30,"
        f"drawtext=text='LIKE and SHARE if this helped!':fontsize=28:fontcolor=0x{TEAL}:x=(w-text_w)/2:y=ih-100"
        f"[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x{DARK}:s=1920x1080:d=5",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-filter_complex", filt,
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-c:a", "aac", "-t", "5", "-pix_fmt", "yuv420p",
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def add_music(input_path, output_path):
    d = dur(input_path)
    music = f"{os.path.dirname(input_path)}/m.mp3"

    # Ambient music
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"sine=f=110:d={d+5}",
        "-af", f"volume=0.015,lowpass=f=250,afade=t=out:st={d-3}:d=3",
        "-c:a", "libmp3lame", music
    ], capture_output=True)

    # Mix
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-i", music,
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:weights=1 0.25[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac",
        output_path
    ], capture_output=True)

def create_video(script, name):
    title = script["title"]
    hook_text = script.get("hook", "Watch this now")
    sections = script["sections"]

    print(f"\n🎬 {title}")

    with tempfile.TemporaryDirectory() as temp:
        parts = []

        # Hook
        print("  → Hook...")
        h = hook(hook_text, temp)
        if h: parts.append(h); print(f"     ✓ {dur(h):.1f}s")

        # Title
        print("  → Title...")
        t = title_card(title, temp)
        if t: parts.append(t); print(f"     ✓ {dur(t):.1f}s")

        # Sections
        total = len(sections)
        for i, sec in enumerate(sections, 1):
            print(f"  → {i}/{total}: {sec['title'][:28]}...")
            stype = sec.get("type", "info")
            if stype == "warning":
                color, accent = "3d0c02", "FFCC00"
            elif stype == "tip":
                color, accent = BLUE, TEAL
            elif stype == "cta":
                color, accent = DARK, ORANGE
            else:
                color, accent = DARK, TEAL

            s = segment(sec["title"], "", sec["dialogue"], i, total, color, accent, temp)
            if s: parts.append(s); print(f"     ✓ {dur(s):.1f}s")

        # CTA
        print("  → CTA...")
        c = cta_card(temp)
        if c: parts.append(c); print(f"     ✓ {dur(c):.1f}s")

        # End
        print("  → End...")
        e = end_screen(temp)
        if e: parts.append(e); print(f"     ✓ {dur(e):.1f}s")

        if not parts:
            print("  ✗ No segments created")
            return None

        # Concat
        print("  → Combining...")
        concat_file = f"{temp}/list.txt"
        with open(concat_file, "w") as f:
            for p in parts:
                f.write(f"file '{p}'\n")

        raw = f"{temp}/raw.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c:v", "libx264", "-c:a", "aac",
            raw
        ], capture_output=True)

        if not os.path.exists(raw):
            print("  ✗ Concat failed")
            return None

        # Music
        print("  → Music...")
        final = f"{OUTPUT}/{name}.mp4"
        add_music(raw, final)

        if os.path.exists(final):
            d = dur(final)
            s = os.path.getsize(final) / (1024*1024)
            print(f"\n✅ {name}.mp4 ({d/60:.1f} min, {s:.1f} MB)")
            return final
        else:
            # Fallback - just copy raw
            subprocess.run(["cp", raw, final])
            if os.path.exists(final):
                print(f"\n✅ {name}.mp4 (no music)")
                return final

    return None

# SCRIPTS
SCRIPTS = {
    "stop-foreclosure": {
        "title": "How to Stop Foreclosure FAST",
        "hook": "STOP - This could save your home",
        "sections": [
            {"title": "Your Bank Has a Secret", "dialogue": "Heres what banks wont tell you. Foreclosure costs them tens of thousands. They would rather work with you. Thats your leverage.", "type": "hook"},
            {"title": "Option 1 - Loan Mod", "dialogue": "First option - loan modification. The bank rewrites your loan. Lower rate. Longer term. Affordable payment. They approve these more than you think.", "type": "tip"},
            {"title": "Option 2 - Forbearance", "dialogue": "Second option - forbearance. Pause payments while you recover. Perfect for job loss or medical issues. Act fast to qualify.", "type": "tip"},
            {"title": "Option 3 - Sell Fast", "dialogue": "Third option - sell to a cash buyer. Keep your equity. Close in days. Walk away with money instead of nothing.", "type": "tip"},
            {"title": "The Fatal Mistake", "dialogue": "The biggest mistake - ignoring it. Every day you wait, you lose options. Dont bury your head. Take action now.", "type": "warning"},
            {"title": "Call Us Now", "dialogue": "Call us today for a free consultation. No pressure. No games. Just real answers about your options.", "type": "cta"}
        ]
    },
    "5-mistakes": {
        "title": "5 Mistakes That Lose Your Home",
        "hook": "Are you making these deadly mistakes?",
        "sections": [
            {"title": "Mistake 1 - Ignoring It", "dialogue": "Ignoring the problem. Those letters are scary. But every day you ignore them, you lose options. The clock is ticking.", "type": "warning"},
            {"title": "Mistake 2 - Closed Mail", "dialogue": "Not opening your mail. Critical deadlines are in those letters. Miss a deadline, lose a right. Open everything.", "type": "warning"},
            {"title": "Mistake 3 - Waiting", "dialogue": "Waiting for a miracle. Hope is not a strategy. Only action works. Nobody is coming to save you.", "type": "warning"},
            {"title": "Mistake 4 - Scammers", "dialogue": "Falling for scammers. Never pay huge upfront fees. Never sign over your deed. If it sounds too good, run.", "type": "warning"},
            {"title": "Mistake 5 - Giving Up", "dialogue": "Giving up too early. Ive seen homes saved days before auction. Fight until the end.", "type": "warning"},
            {"title": "Still Time", "dialogue": "Theres still time. Call us now for a free consultation. That call could save your home.", "type": "cta"}
        ]
    },
    "california-timeline": {
        "title": "CA Foreclosure Timeline",
        "hook": "Know exactly how much time you have",
        "sections": [
            {"title": "The 200 Day Clock", "dialogue": "California foreclosure takes about 200 days. Thats over 6 months. But time flies if you dont use it.", "type": "info"},
            {"title": "Days 1 to 120", "dialogue": "First 120 days - youre delinquent but not in foreclosure. Use this time to negotiate. The bank cant file yet.", "type": "tip"},
            {"title": "Notice of Default", "dialogue": "After 120 days - Notice of Default. The official start. You have 90 days to catch up or find a solution.", "type": "warning"},
            {"title": "Notice of Sale", "dialogue": "No fix? Notice of Sale. Your auction date is set. At least 21 days warning. Final countdown.", "type": "warning"},
            {"title": "Auction Day", "dialogue": "Auction day - home sells to highest bidder. No redemption in California. Once sold, its gone forever.", "type": "warning"},
            {"title": "Act Today", "dialogue": "Wherever you are on this timeline, options exist. Call us now. Lets find your best move.", "type": "cta"}
        ]
    },
    "sell-foreclosure": {
        "title": "Sell During Foreclosure",
        "hook": "Keep your equity - dont lose it all",
        "sections": [
            {"title": "Yes You Can Sell", "dialogue": "Can you sell during foreclosure? Absolutely yes. Legal right until auction day. Most people dont know this.", "type": "tip"},
            {"title": "Why Selling Wins", "dialogue": "Selling beats foreclosure. Keep your equity. Control the timeline. Less credit damage. Win win win.", "type": "tip"},
            {"title": "Cash Buyers Key", "dialogue": "Cash buyers are the secret. We close in 7 days. No banks, no delays. You dont have months.", "type": "tip"},
            {"title": "Auction Nightmare", "dialogue": "Auction is the nightmare. Bank takes your house. Keeps your equity. Youre left with nothing.", "type": "warning"},
            {"title": "Get Your Offer", "dialogue": "Call for a free cash offer today. No repairs. No fees. Just a real number you can count on.", "type": "cta"}
        ]
    },
    "los-angeles": {
        "title": "Stop Foreclosure LA",
        "hook": "LA homeowners - protect your equity",
        "sections": [
            {"title": "LA Market Hot", "dialogue": "LA real estate is on fire. Even in foreclosure, you have serious equity. That money is yours.", "type": "tip"},
            {"title": "High Demand", "dialogue": "Cash buyers are competing for LA properties. That means better offers for you. Fast closings before auction.", "type": "tip"},
            {"title": "All Neighborhoods", "dialogue": "We buy everywhere in LA. The Valley. South LA. Eastside. Westside. Any condition. As-is.", "type": "info"},
            {"title": "Local Experts", "dialogue": "We know LA. We know the courts. We know how to move fast when time is short.", "type": "info"},
            {"title": "Call Today", "dialogue": "LA homeowners - dont lose your equity. Call now for free consultation and cash offer.", "type": "cta"}
        ]
    },
    "san-diego": {
        "title": "Stop Foreclosure SD",
        "hook": "San Diego - save your home or equity",
        "sections": [
            {"title": "SD Values High", "dialogue": "San Diego values are sky high. Your home has equity worth fighting for. Dont give it away.", "type": "tip"},
            {"title": "Military Welcome", "dialogue": "We help military families. PCS orders. Deployment issues. We understand and we move fast.", "type": "info"},
            {"title": "All SD County", "dialogue": "Chula Vista. Oceanside. Escondido. All San Diego County. We buy houses everywhere.", "type": "info"},
            {"title": "Fast Closings", "dialogue": "Need speed? Cash offer in 24 hours. Close in 7 days. No games.", "type": "tip"},
            {"title": "Free Consult", "dialogue": "San Diego homeowners - call today. Free consultation. Free cash offer. Lets save your equity.", "type": "cta"}
        ]
    }
}

if __name__ == "__main__":
    print("=" * 50)
    print("🎬 FINAL Video Generator")
    print("=" * 50)

    for name, script in SCRIPTS.items():
        create_video(script, name)

    print("\n" + "=" * 50)
    print(f"📁 {OUTPUT}")
    print("=" * 50)
