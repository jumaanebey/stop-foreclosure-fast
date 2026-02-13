#!/usr/bin/env python3
"""
Whiteboard Style Video - Sketch filter + reveal animation
Test with existing images
"""
import subprocess
import os
import tempfile

ASSETS = "/Users/jumaanebey/.gemini/antigravity/scratch/visual-prompts"
OUTPUT = "/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/final-videos"
VOICE = "en-US-GuyNeural"

os.makedirs(OUTPUT, exist_ok=True)

def tts(text, path):
    subprocess.run(["edge-tts", "--voice", VOICE, "--rate", "+5%", "--text", text, "--write-media", path], capture_output=True)
    return os.path.exists(path)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except: return 5.0

def make_whiteboard_segment(image_path, dialogue, temp_dir, idx):
    """Create whiteboard-style segment with sketch filter and wipe reveal"""
    audio = f"{temp_dir}/seg{idx}.mp3"
    video = f"{temp_dir}/seg{idx}.mp4"

    if not os.path.exists(image_path):
        print(f"     ⚠ Missing: {image_path}")
        return None

    if not tts(dialogue, audio):
        return None

    d = dur(audio) + 0.5

    # Sketch effect + left-to-right wipe reveal animation
    # edgedetect creates sketch look, negate inverts to white bg
    # The crop with expanding width creates reveal effect
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio,
        "-filter_complex", (
            f"[0:v]scale=1920:1080,"
            # Sketch/pencil effect
            f"edgedetect=low=0.1:high=0.3,negate,"
            # Add slight sepia/warm tone
            f"colorbalance=rs=.1:gs=.05:bs=-.1,"
            # Wipe reveal from left to right
            f"crop=w='min(iw,iw*t/{d*0.7})':h=ih:x=0:y=0,pad=1920:1080:0:0:white,"
            f"fps=30,"
            f"drawtext=text='MyForeclosureSolution.com':fontsize=20:fontcolor=gray@0.4:x=w-text_w-20:y=h-35[v]"
        ),
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
        "-t", str(d),
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def make_cta_whiteboard(image_path, temp_dir):
    """CTA in whiteboard style"""
    audio = f"{temp_dir}/cta.mp3"
    video = f"{temp_dir}/cta.mp4"

    tts("Call us now for your free consultation. We help California homeowners every day.", audio)
    d = dur(audio) + 2

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio,
        "-filter_complex", (
            f"[0:v]scale=1920:1080,"
            f"edgedetect=low=0.1:high=0.3,negate,"
            f"colorbalance=rs=.1:gs=.05:bs=-.1,"
            f"fps=30,"
            # Overlay CTA text
            f"drawbox=x=iw/2-280:y=ih/2-50:w=560:h=100:c=0x333333:t=fill,"
            f"drawtext=text='CALL (949) 565-5285':fontsize=42:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2,"
            f"drawtext=text='Free Consultation':fontsize=28:fontcolor=gray:x=(w-text_w)/2:y=(h-text_h)/2+70[v]"
        ),
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
        "-t", str(d),
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def make_end_whiteboard(image_path, temp_dir):
    """End screen whiteboard style"""
    video = f"{temp_dir}/end.mp4"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-filter_complex", (
            f"[0:v]scale=1920:1080,"
            f"edgedetect=low=0.1:high=0.3,negate,"
            f"colorbalance=rs=.1:gs=.05:bs=-.1,"
            f"fps=30,"
            f"drawtext=text='SUBSCRIBE for more tips!':fontsize=36:fontcolor=0x333333:x=(w-text_w)/2:y=ih/2,"
            f"drawtext=text='Like & Share':fontsize=28:fontcolor=gray:x=(w-text_w)/2:y=ih/2+50[v]"
        ),
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-t", "4", "-pix_fmt", "yuv420p",
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def create_whiteboard_video(name, script):
    """Build whiteboard style video"""
    asset_dir = f"{ASSETS}/{name}"
    title = script["title"]
    hook_text = script["hook"]
    sections = script["sections"]

    print(f"\n🎬 {title} (Whiteboard Style)")

    with tempfile.TemporaryDirectory() as temp:
        parts = []

        # Hook
        print("  → Hook...")
        h = make_whiteboard_segment(f"{asset_dir}/hook.png", hook_text, temp, 0)
        if h: parts.append(h); print(f"     ✓ {dur(h):.1f}s")

        # Title
        print("  → Title...")
        t = make_whiteboard_segment(f"{asset_dir}/title.png", title, temp, 99)
        if t: parts.append(t); print(f"     ✓ {dur(t):.1f}s")

        # Sections
        for i, sec in enumerate(sections, 1):
            print(f"  → Scene {i}: {sec['title'][:25]}...")
            s = make_whiteboard_segment(f"{asset_dir}/scene{i}.png", sec["dialogue"], temp, i)
            if s: parts.append(s); print(f"     ✓ {dur(s):.1f}s")

        # CTA
        print("  → CTA...")
        c = make_cta_whiteboard(f"{asset_dir}/cta.png", temp)
        if c: parts.append(c); print(f"     ✓ {dur(c):.1f}s")

        # End
        print("  → End...")
        e = make_end_whiteboard(f"{asset_dir}/end.png", temp)
        if e: parts.append(e); print(f"     ✓ {dur(e):.1f}s")

        if not parts:
            print("  ✗ No segments")
            return None

        # Concat
        print("  → Combining...")
        concat_file = f"{temp}/list.txt"
        with open(concat_file, "w") as f:
            for p in parts:
                f.write(f"file '{p}'\n")

        final = f"{OUTPUT}/{name}-whiteboard.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c:v", "libx264", "-c:a", "aac", final
        ], capture_output=True)

        if os.path.exists(final):
            d = dur(final)
            s = os.path.getsize(final) / (1024*1024)
            print(f"\n✅ {name}-whiteboard.mp4 ({d/60:.1f} min, {s:.1f} MB)")
            return final

    return None

# Script
SCRIPT = {
    "title": "How to Stop Foreclosure FAST",
    "hook": "STOP - This could save your home",
    "sections": [
        {"title": "Your Bank Has a Secret", "dialogue": "Heres what banks wont tell you. Foreclosure costs them tens of thousands. They would rather work with you. Thats your leverage."},
        {"title": "Option 1 - Loan Mod", "dialogue": "First option - loan modification. The bank rewrites your loan. Lower rate. Longer term. Affordable payment."},
        {"title": "Option 2 - Forbearance", "dialogue": "Second option - forbearance. Pause payments while you recover. Perfect for job loss or medical issues."},
        {"title": "Option 3 - Sell Fast", "dialogue": "Third option - sell to a cash buyer. Keep your equity. Close in days. Walk away with money."},
        {"title": "The Fatal Mistake", "dialogue": "The biggest mistake - ignoring it. Every day you wait, you lose options. Take action now."},
        {"title": "Call Us Now", "dialogue": "Call us today for a free consultation. No pressure. Just real answers."}
    ]
}

if __name__ == "__main__":
    print("=" * 50)
    print("🎬 Whiteboard Style Test")
    print("=" * 50)
    create_whiteboard_video("stop-foreclosure", SCRIPT)
