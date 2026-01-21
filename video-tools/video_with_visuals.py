#!/usr/bin/env python3
"""
Video Generator with AntiGravity Visuals - v2
Smoother zoom, better transitions
"""
import subprocess
import os
import tempfile

ASSETS = "/Users/jumaanebey/.gemini/antigravity/scratch/visual-prompts"
OUTPUT = "/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/final-videos"
VOICE = "en-US-GuyNeural"

os.makedirs(OUTPUT, exist_ok=True)

def tts(text, path):
    subprocess.run(["edge-tts", "--voice", VOICE, "--rate", "+10%", "--text", text, "--write-media", path], capture_output=True)
    return os.path.exists(path)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except: return 5.0

def make_segment_with_image(image_path, dialogue, temp_dir, idx):
    """Create video segment from image + voiceover with smooth subtle zoom"""
    audio = f"{temp_dir}/seg{idx}.mp3"
    video = f"{temp_dir}/seg{idx}.mp4"

    if not os.path.exists(image_path):
        print(f"     ⚠ Missing: {image_path}")
        return None

    if not tts(dialogue, audio):
        return None

    d = dur(audio) + 0.5
    frames = int(d * 30)

    # Very subtle, smooth zoom - only 5% total zoom over duration
    # Using smooth easing with slower rate
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio,
        "-filter_complex", (
            f"[0:v]scale=2000:1125,fps=30,"
            f"zoompan=z='1+0.0003*in':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080,"
            f"fade=t=in:st=0:d=0.5,fade=t=out:st={d-0.5}:d=0.5,"
            f"drawtext=text='MyForeclosureSolution.com':fontsize=22:fontcolor=white@0.5:x=w-text_w-25:y=25[v]"
        ),
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
        "-t", str(d),
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def make_cta_with_image(image_path, temp_dir):
    """Create CTA with image background - no zoom, just overlay"""
    audio = f"{temp_dir}/cta.mp3"
    video = f"{temp_dir}/cta.mp4"

    tts("Call us right now for your free consultation. We help California homeowners every day. That call could change everything.", audio)
    d = dur(audio) + 2

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio,
        "-filter_complex", (
            f"[0:v]scale=1920:1080,fps=30,"
            f"drawbox=x=0:y=0:w=iw:h=ih:c=black@0.65:t=fill,"
            f"drawbox=x=iw/2-320:y=ih/2-70:w=640:h=140:c=0xFF6B35:t=fill,"
            f"drawtext=text='CALL NOW':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-25,"
            f"drawtext=text='(949) 565-5285':fontsize=52:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2+85,"
            f"drawtext=text='MyForeclosureSolution.com':fontsize=34:fontcolor=0x00D4AA:x=(w-text_w)/2:y=(h-text_h)/2+170,"
            f"fade=t=in:st=0:d=0.5[v]"
        ),
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
        "-t", str(d),
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def make_end_with_image(image_path, temp_dir):
    """Create end screen - static with overlay"""
    video = f"{temp_dir}/end.mp4"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-filter_complex", (
            f"[0:v]scale=1920:1080,fps=30,"
            f"drawbox=x=0:y=0:w=iw:h=ih:c=black@0.55:t=fill,"
            f"drawbox=x=iw/2-110:y=ih/2-110:w=220:h=220:c=0xFF0000:t=fill,"
            f"drawtext=text='SUBSCRIBE':fontsize=38:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-12,"
            f"drawtext=text='for more tips':fontsize=24:fontcolor=white@0.8:x=(w-text_w)/2:y=(h-text_h)/2+32,"
            f"drawtext=text='LIKE and SHARE if this helped!':fontsize=30:fontcolor=0x00D4AA:x=(w-text_w)/2:y=ih-110,"
            f"fade=t=in:st=0:d=0.5[v]"
        ),
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-c:a", "aac", "-t", "5", "-pix_fmt", "yuv420p",
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def add_music(input_path, output_path):
    d = dur(input_path)
    music = f"{os.path.dirname(input_path)}/m.mp3"

    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"sine=f=110:d={d+5}",
        "-af", f"volume=0.010,lowpass=f=180,afade=t=in:d=2,afade=t=out:st={d-3}:d=3",
        "-c:a", "libmp3lame", music
    ], capture_output=True)

    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path, "-i", music,
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:weights=1 0.15[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac",
        output_path
    ], capture_output=True)

def create_video(name, script):
    """Build video with visuals"""
    asset_dir = f"{ASSETS}/{name}"
    title = script["title"]
    hook_text = script["hook"]
    sections = script["sections"]

    print(f"\n🎬 {title}")

    with tempfile.TemporaryDirectory() as temp:
        parts = []

        # Hook
        print("  → Hook...")
        h = make_segment_with_image(f"{asset_dir}/hook.png", hook_text, temp, 0)
        if h: parts.append(h); print(f"     ✓ {dur(h):.1f}s")

        # Title
        print("  → Title...")
        t = make_segment_with_image(f"{asset_dir}/title.png", title, temp, 99)
        if t: parts.append(t); print(f"     ✓ {dur(t):.1f}s")

        # Sections
        for i, sec in enumerate(sections, 1):
            print(f"  → Scene {i}: {sec['title'][:25]}...")
            s = make_segment_with_image(f"{asset_dir}/scene{i}.png", sec["dialogue"], temp, i)
            if s: parts.append(s); print(f"     ✓ {dur(s):.1f}s")

        # CTA
        print("  → CTA...")
        c = make_cta_with_image(f"{asset_dir}/cta.png", temp)
        if c: parts.append(c); print(f"     ✓ {dur(c):.1f}s")

        # End
        print("  → End...")
        e = make_end_with_image(f"{asset_dir}/end.png", temp)
        if e: parts.append(e); print(f"     ✓ {dur(e):.1f}s")

        if not parts:
            print("  ✗ No segments")
            return None

        # Concat with crossfade would be ideal but complex - simple concat for now
        print("  → Combining...")
        concat_file = f"{temp}/list.txt"
        with open(concat_file, "w") as f:
            for p in parts:
                f.write(f"file '{p}'\n")

        raw = f"{temp}/raw.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c:v", "libx264", "-c:a", "aac", raw
        ], capture_output=True)

        # Music
        print("  → Music...")
        final = f"{OUTPUT}/{name}-visual.mp4"
        add_music(raw, final)

        if os.path.exists(final):
            d = dur(final)
            s = os.path.getsize(final) / (1024*1024)
            print(f"\n✅ {name}-visual.mp4 ({d/60:.1f} min, {s:.1f} MB)")
            return final

    return None

# SCRIPTS
SCRIPTS = {
    "stop-foreclosure": {
        "title": "How to Stop Foreclosure FAST",
        "hook": "STOP - This could save your home",
        "sections": [
            {"title": "Your Bank Has a Secret", "dialogue": "Heres what banks wont tell you. Foreclosure costs them tens of thousands. They would rather work with you. Thats your leverage."},
            {"title": "Option 1 - Loan Mod", "dialogue": "First option - loan modification. The bank rewrites your loan. Lower rate. Longer term. Affordable payment. They approve these more than you think."},
            {"title": "Option 2 - Forbearance", "dialogue": "Second option - forbearance. Pause payments while you recover. Perfect for job loss or medical issues. Act fast to qualify."},
            {"title": "Option 3 - Sell Fast", "dialogue": "Third option - sell to a cash buyer. Keep your equity. Close in days. Walk away with money instead of nothing."},
            {"title": "The Fatal Mistake", "dialogue": "The biggest mistake - ignoring it. Every day you wait, you lose options. Dont bury your head. Take action now."},
            {"title": "Call Us Now", "dialogue": "Call us today for a free consultation. No pressure. No games. Just real answers about your options."}
        ]
    },
    "5-mistakes": {
        "title": "5 Mistakes That Lose Your Home",
        "hook": "Are you making these deadly mistakes?",
        "sections": [
            {"title": "Mistake 1 - Ignoring It", "dialogue": "Ignoring the problem. Those letters are scary. But every day you ignore them, you lose options. The clock is ticking."},
            {"title": "Mistake 2 - Closed Mail", "dialogue": "Not opening your mail. Critical deadlines are in those letters. Miss a deadline, lose a right. Open everything."},
            {"title": "Mistake 3 - Waiting", "dialogue": "Waiting for a miracle. Hope is not a strategy. Only action works. Nobody is coming to save you."},
            {"title": "Mistake 4 - Scammers", "dialogue": "Falling for scammers. Never pay huge upfront fees. Never sign over your deed. If it sounds too good, run."},
            {"title": "Mistake 5 - Giving Up", "dialogue": "Giving up too early. Ive seen homes saved days before auction. Fight until the end."},
            {"title": "Still Time", "dialogue": "Theres still time. Call us now for a free consultation. That call could save your home."}
        ]
    }
}

if __name__ == "__main__":
    print("=" * 50)
    print("🎬 Video Generator v2 - Smoother Zoom")
    print("=" * 50)

    for name in ["stop-foreclosure", "5-mistakes"]:
        if name in SCRIPTS:
            create_video(name, SCRIPTS[name])

    print("\n" + "=" * 50)
    print(f"📁 {OUTPUT}")
    print("=" * 50)
