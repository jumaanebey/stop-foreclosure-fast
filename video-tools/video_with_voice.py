#!/usr/bin/env python3
"""
Video Generator with AI Voice (Edge TTS - Free)
Creates faceless videos with professional voiceover
"""

import subprocess
import os
import re
import tempfile
import asyncio
from pathlib import Path

# Voice options (all free):
# en-US-AndrewNeural - Warm, Confident (recommended)
# en-US-BrianNeural - Approachable, Casual
# en-US-ChristopherNeural - Reliable, Authority
# en-US-GuyNeural - Passion
VOICE = "en-US-AndrewNeural"
RATE = "+0%"  # Speed: -50% to +100%


async def generate_audio(text, output_path, voice=VOICE, rate=RATE):
    """Generate audio from text using Edge TTS"""
    import edge_tts

    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)
    return output_path


def get_audio_duration(audio_path):
    """Get duration of audio file in seconds"""
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
           '-of', 'default=noprint_wrappers=1:nokey=1', audio_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def create_video_with_voice(script_path, output_path):
    """Create a video with AI voiceover from a YouTube script"""

    # Read script
    with open(script_path, 'r') as f:
        content = f.read()

    # Get title
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Video"

    # Parse sections and extract dialogue
    sections = []
    pattern = r'^## (.+?) \((\d+):(\d+)-(\d+):(\d+)\)'

    current_pos = 0
    matches = list(re.finditer(pattern, content, re.MULTILINE))

    for i, match in enumerate(matches):
        section_name = match.group(1)

        # Find section text until next section
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section_text = content[start:end]

        # Extract quoted dialogue (what to speak)
        quotes = re.findall(r'"([^"]+)"', section_text)
        dialogue = ' '.join(quotes) if quotes else ""

        # Clean up dialogue
        dialogue = re.sub(r'\[.*?\]', '', dialogue)  # Remove [Name] etc
        dialogue = dialogue.strip()

        if dialogue:
            sections.append({
                'name': section_name,
                'dialogue': dialogue
            })

    print(f"Title: {title}")
    print(f"Sections with dialogue: {len(sections)}")

    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    clips = []

    # Title card (4 seconds, no voice)
    title_clip = os.path.join(temp_dir, "00_title.mp4")
    safe_title = title[:50].replace("'", "").replace('"', '').replace(':', ' -')

    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', 'color=c=0x1a1a2e:s=1920x1080:d=4:r=30',
        '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-vf', f"drawtext=fontfile=/System/Library/Fonts/Helvetica.ttc:text='{safe_title}':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2",
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', '-shortest',
        '-pix_fmt', 'yuv420p', '-t', '4',
        title_clip
    ]
    subprocess.run(cmd, capture_output=True)
    clips.append(title_clip)
    print(f"  Created: Title card (4s)")

    # Create each section with voice
    for i, section in enumerate(sections):
        print(f"  Processing: {section['name']}...")

        # Generate audio
        audio_path = os.path.join(temp_dir, f"{i+1:02d}_audio.mp3")
        asyncio.run(generate_audio(section['dialogue'], audio_path))

        # Get audio duration
        duration = get_audio_duration(audio_path) + 1  # Add 1 second padding

        # Create video with audio
        clip_path = os.path.join(temp_dir, f"{i+1:02d}_{section['name'][:15].replace(' ', '_')}.mp4")
        safe_name = section['name'].replace("'", "").replace('"', '').replace(':', ' -')

        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi', '-i', f'color=c=0x0f0f23:s=1920x1080:d={duration}:r=30',
            '-i', audio_path,
            '-vf', f"drawtext=fontfile=/System/Library/Fonts/Helvetica.ttc:text='{safe_name}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.6:boxborderw=15",
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
            '-c:a', 'aac', '-b:a', '128k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            clip_path
        ]
        subprocess.run(cmd, capture_output=True)
        clips.append(clip_path)
        print(f"    Done: {section['name']} ({duration:.1f}s)")

    # Create concat file
    concat_file = os.path.join(temp_dir, "concat.txt")
    with open(concat_file, 'w') as f:
        for clip in clips:
            f.write(f"file '{clip}'\n")

    # Concatenate all clips
    print("Concatenating clips...")
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0',
        '-i', concat_file,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        size = os.path.getsize(output_path) / (1024 * 1024)
        duration = get_audio_duration(output_path)
        print(f"\n✅ Video created: {output_path}")
        print(f"   Duration: {duration/60:.1f} minutes")
        print(f"   Size: {size:.1f} MB")
        print(f"   Voice: {VOICE}")
        return output_path
    else:
        print(f"Error: {result.stderr}")
        return None


if __name__ == "__main__":
    script = "/Users/jumaanebey/Documents/stop-foreclosure-fast/youtube-scripts/01-stop-foreclosure-california.md"
    output = "/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/test-outputs/foreclosure-WITH-VOICE.mp4"

    create_video_with_voice(script, output)
