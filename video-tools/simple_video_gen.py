#!/usr/bin/env python3
"""
Simple Video Generator - Creates working videos from scripts
"""

import subprocess
import os
import re
import tempfile
from pathlib import Path


def create_video_from_script(script_path, output_path):
    """Create a video from a YouTube script"""

    # Read script
    with open(script_path, 'r') as f:
        content = f.read()

    # Get title
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Video"

    # Parse sections with timestamps
    sections = []
    pattern = r'^## (.+?) \((\d+):(\d+)-(\d+):(\d+)\)'

    for match in re.finditer(pattern, content, re.MULTILINE):
        section_name = match.group(1)
        start_sec = int(match.group(2)) * 60 + int(match.group(3))
        end_sec = int(match.group(4)) * 60 + int(match.group(5))
        duration = end_sec - start_sec

        sections.append({
            'name': section_name,
            'duration': duration
        })

    print(f"Title: {title}")
    print(f"Sections: {len(sections)}")

    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    clips = []

    # Title card (4 seconds)
    title_clip = os.path.join(temp_dir, "00_title.mp4")
    safe_title = title[:50].replace("'", "").replace('"', '').replace(':', ' -')

    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', 'color=c=0x1a1a2e:s=1920x1080:d=4:r=30',
        '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-vf', f"drawtext=fontfile=/System/Library/Fonts/Helvetica.ttc:text='{safe_title}':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2",
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', '-shortest',
        '-pix_fmt', 'yuv420p',
        '-t', '4',
        title_clip
    ]
    subprocess.run(cmd, capture_output=True)
    clips.append(title_clip)
    print(f"  Created: Title card")

    # Create each section
    for i, section in enumerate(sections):
        clip_path = os.path.join(temp_dir, f"{i+1:02d}_{section['name'][:20].replace(' ', '_')}.mp4")
        safe_name = section['name'].replace("'", "").replace('"', '').replace(':', ' -')

        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi', '-i', f"color=c=0x0f0f23:s=1920x1080:d={section['duration']}:r=30",
            '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
            '-vf', f"drawtext=fontfile=/System/Library/Fonts/Helvetica.ttc:text='{safe_name}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.6:boxborderw=15",
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
            '-c:a', 'aac', '-shortest',
            '-pix_fmt', 'yuv420p',
            '-t', str(section['duration']),
            clip_path
        ]
        subprocess.run(cmd, capture_output=True)
        clips.append(clip_path)
        print(f"  Created: {section['name']}")

    # Create concat file
    concat_file = os.path.join(temp_dir, "concat.txt")
    with open(concat_file, 'w') as f:
        for clip in clips:
            f.write(f"file '{clip}'\n")

    # Concatenate
    print("Concatenating clips...")
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0',
        '-i', concat_file,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\nVideo created: {output_path}")
        print(f"Size: {size:.1f} MB")
        return output_path
    else:
        print(f"Error: {result.stderr}")
        return None


if __name__ == "__main__":
    script = "/Users/jumaanebey/Documents/stop-foreclosure-fast/youtube-scripts/01-stop-foreclosure-california.md"
    output = "/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/test-outputs/foreclosure-video-v3.mp4"

    create_video_from_script(script, output)
