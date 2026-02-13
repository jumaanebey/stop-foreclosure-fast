#!/usr/bin/env python3
"""
Video Generator with AI Voice - V2 (Fixed)
Creates full audio first, then syncs with video
"""

import subprocess
import os
import re
import tempfile
import asyncio
from pathlib import Path

VOICE = "en-US-AndrewNeural"  # Warm, confident
RATE = "+0%"


async def generate_audio(text, output_path, voice=VOICE, rate=RATE):
    """Generate audio from text using Edge TTS"""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)


def get_duration(file_path):
    """Get duration of audio/video file"""
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
           '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def extract_full_script(script_path):
    """Extract all dialogue from script in order"""
    with open(script_path, 'r') as f:
        content = f.read()

    # Get title
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Video"

    # Extract all quoted dialogue
    all_dialogue = []

    # Find section headers and their dialogue
    pattern = r'^## (.+?) \((\d+):(\d+)-(\d+):(\d+)\)'
    matches = list(re.finditer(pattern, content, re.MULTILINE))

    for i, match in enumerate(matches):
        section_name = match.group(1)

        # Find section text
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section_text = content[start:end]

        # Extract quotes
        quotes = re.findall(r'"([^"]+)"', section_text)
        if quotes:
            dialogue = ' '.join(quotes)
            dialogue = re.sub(r'\[.*?\]', '', dialogue)  # Remove [Name] etc
            all_dialogue.append(dialogue.strip())

    full_script = ' ... '.join(all_dialogue)  # Pause between sections
    return title, full_script


def create_video_with_voice(script_path, output_path):
    """Create video with synced AI voice"""

    title, full_script = extract_full_script(script_path)
    print(f"Title: {title}")
    print(f"Script length: {len(full_script)} chars")

    temp_dir = tempfile.mkdtemp()

    # Step 1: Generate full audio
    print("\n1. Generating AI voiceover...")
    audio_path = os.path.join(temp_dir, "voiceover.mp3")
    asyncio.run(generate_audio(full_script, audio_path))

    audio_duration = get_duration(audio_path)
    print(f"   Audio duration: {audio_duration:.1f}s ({audio_duration/60:.1f} min)")

    # Step 2: Create video (dark background + title)
    print("\n2. Creating video background...")
    video_duration = audio_duration + 6  # 4s title + 2s outro padding

    video_path = os.path.join(temp_dir, "video_only.mp4")
    safe_title = title[:45].replace("'", "").replace('"', '').replace(':', ' -')

    # Complex filter: title for 4s, then section name
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', f'color=c=0x0f0f23:s=1920x1080:d={video_duration}:r=30',
        '-vf', (
            f"drawtext=fontfile=/System/Library/Fonts/Helvetica.ttc:"
            f"text='{safe_title}':"
            f"fontcolor=white:fontsize=54:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"enable='lt(t,4)',"
            f"drawtext=fontfile=/System/Library/Fonts/Helvetica.ttc:"
            f"text='My Foreclosure Solution':"
            f"fontcolor=0x888888:fontsize=28:"
            f"x=(w-text_w)/2:y=h-80"
        ),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-pix_fmt', 'yuv420p',
        video_path
    ]
    subprocess.run(cmd, capture_output=True)
    print(f"   Video duration: {video_duration:.1f}s")

    # Step 3: Combine video + audio
    print("\n3. Combining video and audio...")
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac', '-b:a', '192k',
        '-map', '0:v:0', '-map', '1:a:0',
        '-shortest',
        '-movflags', '+faststart',
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and os.path.exists(output_path):
        size = os.path.getsize(output_path) / (1024 * 1024)
        final_duration = get_duration(output_path)
        print(f"\n✅ SUCCESS!")
        print(f"   Output: {output_path}")
        print(f"   Duration: {final_duration/60:.1f} minutes")
        print(f"   Size: {size:.1f} MB")
        print(f"   Voice: {VOICE}")
        return output_path
    else:
        print(f"Error: {result.stderr[-500:]}")
        return None


if __name__ == "__main__":
    script = "/Users/jumaanebey/Documents/stop-foreclosure-fast/youtube-scripts/01-stop-foreclosure-california.md"
    output = "/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/test-outputs/foreclosure-WITH-VOICE.mp4"

    create_video_with_voice(script, output)
