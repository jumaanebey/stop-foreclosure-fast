#!/usr/bin/env python3
"""
VideoScribe Style - Drawing hand animation + social media optimized
"""
import subprocess
import os
import tempfile
import urllib.request

ASSETS = "/Users/jumaanebey/.gemini/antigravity/scratch/visual-prompts"
OUTPUT = "/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/final-videos"
HAND_DIR = "/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/assets"
VOICE = "en-US-GuyNeural"

os.makedirs(OUTPUT, exist_ok=True)
os.makedirs(HAND_DIR, exist_ok=True)

def create_hand_image():
    """Create a simple pen/marker cursor using ffmpeg"""
    hand_path = f"{HAND_DIR}/pen.png"
    if not os.path.exists(hand_path):
        # Create a simple pen shape
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=black@0:s=80x80:d=1",
            "-vf", (
                "format=rgba,"
                "geq=r='0':g='0':b='0':a='if(lt(hypot(X-60,Y-20),15),255,0)'"
            ),
            "-frames:v", "1",
            hand_path
        ]
        subprocess.run(cmd, capture_output=True)
    return hand_path

def tts(text, path):
    subprocess.run(["edge-tts", "--voice", VOICE, "--rate", "+8%", "--text", text, "--write-media", path], capture_output=True)
    return os.path.exists(path)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except: return 5.0

def create_pen_sound(duration, output_path):
    """Create pen scratching sound effect"""
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"anoisesrc=d={duration}:c=pink:a=0.02",
        "-af", "highpass=f=2000,lowpass=f=8000,tremolo=f=15:d=0.4",
        "-c:a", "libmp3lame",
        output_path
    ]
    subprocess.run(cmd, capture_output=True)

def make_drawing_segment(image_path, dialogue, temp_dir, idx, is_short=False):
    """Create segment with drawing animation - hand moves across revealing image"""
    audio = f"{temp_dir}/seg{idx}.mp3"
    video = f"{temp_dir}/seg{idx}.mp4"
    pen_sound = f"{temp_dir}/pen{idx}.mp3"

    if not os.path.exists(image_path):
        print(f"     ⚠ Missing: {os.path.basename(image_path)}")
        return None

    if not tts(dialogue, audio):
        return None

    d = dur(audio) + 0.3
    reveal_time = min(d * 0.5, 3)  # Drawing takes 50% of time, max 3s

    # Create pen scratch sound
    create_pen_sound(reveal_time, pen_sound)

    # Dimensions based on format
    if is_short:
        w, h = 1080, 1920  # Vertical
    else:
        w, h = 1920, 1080  # Horizontal

    # Drawing reveal with moving "pen point" indicator
    # The pen point moves left-to-right while image reveals
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio,
        "-i", pen_sound,
        "-filter_complex", (
            f"[0:v]scale={w}:{h},fps=30,"
            # Diagonal wipe reveal (more natural drawing feel)
            f"geq=lum='if(lt(X+Y*0.3, (W+H*0.3)*min(T/{reveal_time},1)), lum(X,Y), 255)':"
            f"cb='if(lt(X+Y*0.3, (W+H*0.3)*min(T/{reveal_time},1)), cb(X,Y), 128)':"
            f"cr='if(lt(X+Y*0.3, (W+H*0.3)*min(T/{reveal_time},1)), cr(X,Y), 128)',"
            # Draw a "pen tip" dot that moves with the reveal
            f"drawbox=x='min(T/{reveal_time},1)*W-10':y='min(T/{reveal_time},1)*H*0.3':w=8:h=8:c=0x333333@'if(lt(T,{reveal_time}),0.8,0)':t=fill,"
            # Watermark
            f"drawtext=text='MyForeclosureSolution.com':fontsize=16:fontcolor=0x666666@0.4:x=10:y=h-25[v];"
            # Mix audio with pen sound
            f"[1:a][2:a]amix=inputs=2:duration=first:weights=1 0.3[a]"
        ),
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
        "-t", str(d),
        video
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Fallback if geq fails
    if not os.path.exists(video):
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", image_path,
            "-i", audio,
            "-filter_complex", (
                f"[0:v]scale={w}:{h},fps=30,"
                f"fade=t=in:st=0:d=0.6,"
                f"drawtext=text='MyForeclosureSolution.com':fontsize=16:fontcolor=0x666666@0.4:x=10:y=h-25[v]"
            ),
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
            "-t", str(d),
            video
        ]
        subprocess.run(cmd, capture_output=True)

    return video if os.path.exists(video) else None

def make_cta_drawing(image_path, temp_dir, is_short=False):
    """CTA screen"""
    audio = f"{temp_dir}/cta.mp3"
    video = f"{temp_dir}/cta.mp4"

    tts("Call now for your free consultation!", audio)
    d = dur(audio) + 1.5

    if is_short:
        w, h = 1080, 1920
        box_x, box_y, box_w, box_h = 190, 1200, 700, 120
        text_y = 1235
    else:
        w, h = 1920, 1080
        box_x, box_y, box_w, box_h = 560, 700, 800, 100
        text_y = 730

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio,
        "-filter_complex", (
            f"[0:v]scale={w}:{h},fps=30,"
            f"drawbox=x={box_x}:y={box_y}:w={box_w}:h={box_h}:c=0x333333:t=fill,"
            f"drawtext=text='(949) 565-5285':fontsize=48:fontcolor=white:x=(w-text_w)/2:y={text_y},"
            f"fade=t=in:st=0:d=0.4[v]"
        ),
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
        "-t", str(d),
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def make_end_drawing(image_path, temp_dir, is_short=False):
    """End screen"""
    video = f"{temp_dir}/end.mp4"

    if is_short:
        w, h = 1080, 1920
    else:
        w, h = 1920, 1080

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-filter_complex", (
            f"[0:v]scale={w}:{h},fps=30,"
            f"fade=t=in:st=0:d=0.4[v]"
        ),
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-t", "3", "-pix_fmt", "yuv420p",
        video
    ]
    subprocess.run(cmd, capture_output=True)
    return video if os.path.exists(video) else None

def add_music(input_path, output_path):
    d = dur(input_path)
    music = f"{os.path.dirname(input_path)}/m.mp3"

    # Upbeat background music
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"sine=f=165:d={d+5}",
        "-af", f"volume=0.006,lowpass=f=250,tremolo=f=2:d=0.2,afade=t=in:d=1,afade=t=out:st={d-2}:d=2",
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

def create_video(name, script, is_short=False):
    """Build video - horizontal or vertical"""
    asset_dir = f"{ASSETS}/{name}"
    title = script["title"]
    hook_text = script["hook"]
    sections = script["sections"]

    format_type = "SHORT" if is_short else "FULL"
    print(f"\n🎬 {title} ({format_type})")

    with tempfile.TemporaryDirectory() as temp:
        parts = []

        # Hook
        print("  → Hook...")
        h = make_drawing_segment(f"{asset_dir}/hook.png", hook_text, temp, 0, is_short)
        if h: parts.append(h); print(f"     ✓ {dur(h):.1f}s")

        # Title
        print("  → Title...")
        t = make_drawing_segment(f"{asset_dir}/title.png", title, temp, 99, is_short)
        if t: parts.append(t); print(f"     ✓ {dur(t):.1f}s")

        # Sections (limit for shorts)
        max_sections = 3 if is_short else len(sections)
        for i, sec in enumerate(sections[:max_sections], 1):
            print(f"  → Scene {i}...")
            s = make_drawing_segment(f"{asset_dir}/scene{i}.png", sec["dialogue"], temp, i, is_short)
            if s: parts.append(s); print(f"     ✓ {dur(s):.1f}s")

        # CTA
        print("  → CTA...")
        c = make_cta_drawing(f"{asset_dir}/cta.png", temp, is_short)
        if c: parts.append(c); print(f"     ✓ {dur(c):.1f}s")

        # End
        print("  → End...")
        e = make_end_drawing(f"{asset_dir}/end.png", temp, is_short)
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
        suffix = "-short" if is_short else "-scribe"
        final = f"{OUTPUT}/{name}{suffix}.mp4"
        add_music(raw, final)

        if os.path.exists(final):
            d = dur(final)
            s = os.path.getsize(final) / (1024*1024)
            print(f"\n✅ {name}{suffix}.mp4 ({d:.0f}s, {s:.1f} MB)")
            return final

    return None

SCRIPTS = {
    "stop-foreclosure": {
        "title": "How to Stop Foreclosure FAST",
        "hook": "STOP - This could save your home",
        "sections": [
            {"title": "Secret", "dialogue": "Banks dont want to foreclose. It costs them thousands. Thats your leverage."},
            {"title": "Loan Mod", "dialogue": "Option one - loan modification. Lower rate. Lower payment."},
            {"title": "Forbearance", "dialogue": "Option two - pause payments while you recover."},
            {"title": "Sell Fast", "dialogue": "Option three - sell fast. Keep your equity."},
            {"title": "Mistake", "dialogue": "Biggest mistake? Ignoring it. Act now."},
            {"title": "Call", "dialogue": "Call today. Free consultation."}
        ]
    },
    "5-mistakes": {
        "title": "5 Mistakes That Lose Your Home",
        "hook": "Are you making these mistakes?",
        "sections": [
            {"title": "Ignore", "dialogue": "Mistake one - ignoring the problem. Every day you wait, you lose options."},
            {"title": "Mail", "dialogue": "Mistake two - not opening mail. Deadlines are in there."},
            {"title": "Wait", "dialogue": "Mistake three - waiting for a miracle. Action is the only answer."},
            {"title": "Scam", "dialogue": "Mistake four - scammers. Never pay upfront fees."},
            {"title": "Quit", "dialogue": "Mistake five - giving up too early. Fight until the end."},
            {"title": "Hope", "dialogue": "Theres still time. Call us now."}
        ]
    }
}

if __name__ == "__main__":
    print("=" * 50)
    print("🎬 VideoScribe Style Generator")
    print("=" * 50)

    for name in ["stop-foreclosure", "5-mistakes"]:
        # Full horizontal version
        create_video(name, SCRIPTS[name], is_short=False)
        # Vertical short version
        create_video(name, SCRIPTS[name], is_short=True)

    print("\n" + "=" * 50)
    print(f"📁 {OUTPUT}")
    print("=" * 50)
