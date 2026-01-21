#!/usr/bin/env python3
"""
Whiteboard Video Generator - With reveal/wipe animation
For whiteboard-style images from AntiGravity
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
    """Create segment with left-to-right reveal animation"""
    audio = f"{temp_dir}/seg{idx}.mp3"
    video = f"{temp_dir}/seg{idx}.mp4"

    if not os.path.exists(image_path):
        print(f"     ⚠ Missing: {os.path.basename(image_path)}")
        return None

    if not tts(dialogue, audio):
        return None

    d = dur(audio) + 0.5
    reveal_time = min(d * 0.6, 4)  # Reveal takes 60% of duration, max 4 seconds

    # Left-to-right wipe reveal + subtle zoom
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio,
        "-filter_complex", (
            f"[0:v]scale=1920:1080,fps=30,"
            # Wipe reveal from left
            f"geq=lum='if(lt(X,W*min(T/{reveal_time},1)),lum(X,Y),255)':"
            f"cb='if(lt(X,W*min(T/{reveal_time},1)),cb(X,Y),128)':"
            f"cr='if(lt(X,W*min(T/{reveal_time},1)),cr(X,Y),128)',"
            # Watermark
            f"drawtext=text='MyForeclosureSolution.com':fontsize=18:fontcolor=0x666666@0.5:x=w-text_w-15:y=h-30[v]"
        ),
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
        "-t", str(d),
        video
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Fallback if geq filter fails
    if not os.path.exists(video):
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", image_path,
            "-i", audio,
            "-filter_complex", (
                f"[0:v]scale=1920:1080,fps=30,"
                f"fade=t=in:st=0:d=0.8,"
                f"drawtext=text='MyForeclosureSolution.com':fontsize=18:fontcolor=0x666666@0.5:x=w-text_w-15:y=h-30[v]"
            ),
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "22",
            "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
            "-t", str(d),
            video
        ]
        subprocess.run(cmd, capture_output=True)

    return video if os.path.exists(video) else None

def make_cta(image_path, temp_dir):
    """CTA with overlay"""
    audio = f"{temp_dir}/cta.mp3"
    video = f"{temp_dir}/cta.mp4"

    tts("Call us now for your free consultation. We help California homeowners every day.", audio)
    d = dur(audio) + 2

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio,
        "-filter_complex", (
            f"[0:v]scale=1920:1080,fps=30,"
            f"drawbox=x=iw/2-260:y=ih/2+120:w=520:h=90:c=0x333333:t=fill,"
            f"drawtext=text='(949) 565-5285':fontsize=44:fontcolor=white:x=(w-text_w)/2:y=ih/2+140,"
            f"drawtext=text='FREE Consultation':fontsize=24:fontcolor=0x666666:x=(w-text_w)/2:y=ih/2+220,"
            f"fade=t=in:st=0:d=0.5[v]"
        ),
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
        "-t", str(d),
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def make_end(image_path, temp_dir):
    """End screen"""
    video = f"{temp_dir}/end.mp4"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-filter_complex", (
            f"[0:v]scale=1920:1080,fps=30,"
            f"fade=t=in:st=0:d=0.5[v]"
        ),
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-c:a", "aac", "-t", "4", "-pix_fmt", "yuv420p",
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def add_music(input_path, output_path):
    d = dur(input_path)
    music = f"{os.path.dirname(input_path)}/m.mp3"

    # Soft ambient music
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"sine=f=130:d={d+5}",
        "-af", f"volume=0.008,lowpass=f=200,afade=t=in:d=2,afade=t=out:st={d-3}:d=3",
        "-c:a", "libmp3lame", music
    ], capture_output=True)

    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path, "-i", music,
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:weights=1 0.12[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac",
        output_path
    ], capture_output=True)

def create_video(name, script):
    asset_dir = f"{ASSETS}/{name}"
    title = script["title"]
    hook_text = script["hook"]
    sections = script["sections"]

    print(f"\n🎬 {title}")

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
        c = make_cta(f"{asset_dir}/cta.png", temp)
        if c: parts.append(c); print(f"     ✓ {dur(c):.1f}s")

        # End
        print("  → End...")
        e = make_end(f"{asset_dir}/end.png", temp)
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

        raw = f"{temp}/raw.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c:v", "libx264", "-c:a", "aac", raw
        ], capture_output=True)

        # Music
        print("  → Music...")
        final = f"{OUTPUT}/{name}-whiteboard.mp4"
        add_music(raw, final)

        if os.path.exists(final):
            d = dur(final)
            s = os.path.getsize(final) / (1024*1024)
            print(f"\n✅ {name}-whiteboard.mp4 ({d/60:.1f} min, {s:.1f} MB)")
            return final

    return None

SCRIPTS = {
    "stop-foreclosure": {
        "title": "How to Stop Foreclosure FAST",
        "hook": "STOP - This could save your home",
        "sections": [
            {"title": "Your Bank Has a Secret", "dialogue": "Heres what banks wont tell you. Foreclosure costs them tens of thousands. They would rather work with you."},
            {"title": "Loan Modification", "dialogue": "First option - loan modification. The bank rewrites your loan. Lower rate. Longer term. Affordable payment."},
            {"title": "Forbearance", "dialogue": "Second option - forbearance. Pause payments while you recover. Perfect for job loss or medical issues."},
            {"title": "Sell Fast", "dialogue": "Third option - sell to a cash buyer. Keep your equity. Close in days. Walk away with money."},
            {"title": "The Fatal Mistake", "dialogue": "The biggest mistake - ignoring it. Every day you wait, you lose options. Take action now."},
            {"title": "Call Us Now", "dialogue": "Call us today for a free consultation. No pressure. Just real answers."}
        ]
    },
    "5-mistakes": {
        "title": "5 Mistakes That Lose Your Home",
        "hook": "Are you making these deadly mistakes?",
        "sections": [
            {"title": "Ignoring It", "dialogue": "Mistake one - ignoring the problem. Those letters are scary. But every day you ignore them, you lose options."},
            {"title": "Closed Mail", "dialogue": "Mistake two - not opening your mail. Critical deadlines are in those letters. Miss a deadline, lose a right."},
            {"title": "Waiting", "dialogue": "Mistake three - waiting for a miracle. Hope is not a strategy. Only action works."},
            {"title": "Scammers", "dialogue": "Mistake four - falling for scammers. Never pay huge upfront fees. Never sign over your deed."},
            {"title": "Giving Up", "dialogue": "Mistake five - giving up too early. Homes have been saved days before auction. Fight until the end."},
            {"title": "Still Time", "dialogue": "Theres still time. Call us now for a free consultation. That call could save your home."}
        ]
    }
}

if __name__ == "__main__":
    print("=" * 50)
    print("🎬 Whiteboard Video Generator")
    print("=" * 50)

    for name in ["stop-foreclosure", "5-mistakes"]:
        create_video(name, SCRIPTS[name])

    print("\n" + "=" * 50)
    print(f"📁 {OUTPUT}")
    print("=" * 50)
