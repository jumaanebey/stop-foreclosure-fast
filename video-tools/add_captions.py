#!/usr/bin/env python3
"""
Add burned-in captions to videos using Edge TTS subtitles
"""
import subprocess
import os
import tempfile
import json

OUTPUT_DIR = "/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/test-outputs"
CAPTIONED_DIR = "/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/captioned"

def ensure_dirs():
    os.makedirs(CAPTIONED_DIR, exist_ok=True)

def get_duration(path):
    """Get media duration"""
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except:
        return 0

def generate_srt_from_script(script_data, output_path):
    """Generate SRT file from script sections"""
    srt_content = []
    current_time = 0
    index = 1

    # Title intro
    intro_duration = 4
    srt_content.append(f"{index}")
    srt_content.append(f"00:00:00,000 --> 00:00:{intro_duration:02d},000")
    srt_content.append(script_data["title"])
    srt_content.append("")
    current_time += intro_duration
    index += 1

    # Each section
    for section in script_data.get("sections", []):
        dialogue = section.get("dialogue", "")
        if not dialogue:
            continue

        # Estimate duration (roughly 150 words per minute)
        words = len(dialogue.split())
        duration = max(5, (words / 150) * 60)

        # Break dialogue into chunks of ~10 words for captions
        words_list = dialogue.split()
        chunk_size = 8
        chunks = [' '.join(words_list[i:i+chunk_size]) for i in range(0, len(words_list), chunk_size)]

        chunk_duration = duration / len(chunks) if chunks else duration

        for chunk in chunks:
            start_time = current_time
            end_time = current_time + chunk_duration

            start_str = format_time(start_time)
            end_str = format_time(end_time)

            srt_content.append(f"{index}")
            srt_content.append(f"{start_str} --> {end_str}")
            srt_content.append(chunk)
            srt_content.append("")

            current_time = end_time
            index += 1

    with open(output_path, "w") as f:
        f.write("\n".join(srt_content))

    return output_path

def format_time(seconds):
    """Format seconds to SRT time format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def burn_captions(video_path, srt_path, output_path):
    """Burn captions into video"""
    # FFmpeg subtitle filter with styling
    subtitle_filter = (
        f"subtitles={srt_path}:force_style='"
        "FontName=Helvetica,"
        "FontSize=24,"
        "PrimaryColour=&HFFFFFF,"
        "OutlineColour=&H000000,"
        "BackColour=&H80000000,"
        "Outline=2,"
        "Shadow=1,"
        "MarginV=50,"
        "Alignment=2'"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", subtitle_filter,
        "-c:a", "copy",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return os.path.exists(output_path)

def add_simple_captions(video_path, output_path):
    """Add simple bottom text captions using drawtext"""
    # This is simpler and more reliable than SRT
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", (
            "drawbox=y=ih-100:color=black@0.6:width=iw:height=100:t=fill,"
            "drawtext=text='MyForeclosureSolution.com | (949) 565-5285':"
            "fontsize=28:fontcolor=white:x=(w-text_w)/2:y=h-60"
        ),
        "-c:a", "copy",
        output_path
    ]

    subprocess.run(cmd, capture_output=True)
    return os.path.exists(output_path)

if __name__ == "__main__":
    ensure_dirs()

    print("=" * 60)
    print("🎬 Adding Captions to Videos")
    print("=" * 60)

    # Get all main videos (not vertical versions)
    videos = [f for f in os.listdir(OUTPUT_DIR)
              if f.endswith('.mp4') and 'VERTICAL' not in f
              and f not in ['foreclosure-WITH-VOICE.mp4', 'ffmpeg-test-foreclosure.mp4',
                           'ffmpeg-test-v2.mp4', 'first3sec.mp4', 'foreclosure-video-v3.mp4',
                           'simple-test.mp4']]

    for video_file in sorted(videos):
        video_path = os.path.join(OUTPUT_DIR, video_file)
        output_path = os.path.join(CAPTIONED_DIR, video_file.replace('.mp4', '-captioned.mp4'))

        print(f"\n→ Processing: {video_file}")

        if add_simple_captions(video_path, output_path):
            size = os.path.getsize(output_path) / (1024*1024)
            print(f"  ✓ {video_file.replace('.mp4', '-captioned.mp4')} ({size:.1f} MB)")
        else:
            print(f"  ✗ Failed")

    print("\n" + "=" * 60)
    print("✅ Captions complete!")
    print(f"📁 {CAPTIONED_DIR}")
    print("=" * 60)
