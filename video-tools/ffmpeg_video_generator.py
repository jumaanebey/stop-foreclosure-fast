#!/usr/bin/env python3
"""
FFmpeg-based Faceless Video Generator
Creates professional videos from scripts using:
- Background images/stock footage
- Text overlays with animations
- AI voice-over (requires ElevenLabs or local TTS)
- Music/sound effects

100% FREE - No watermarks, no limits
"""

import subprocess
import os
import json
import re
import tempfile
from pathlib import Path


class FFmpegVideoGenerator:
    def __init__(self, output_dir="./outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = tempfile.mkdtemp()

        # Video settings
        self.width = 1920
        self.height = 1080
        self.fps = 30
        self.font = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

    def parse_script(self, script_path):
        """Parse a YouTube script markdown file into sections"""
        with open(script_path, 'r') as f:
            content = f.read()

        sections = []
        current_section = None
        current_text = []

        for line in content.split('\n'):
            # Check for section headers like ## HOOK (0:00-0:05)
            section_match = re.match(r'^## (.+?) \((\d+:\d+)-(\d+:\d+)\)', line)
            if section_match:
                if current_section:
                    sections.append({
                        'title': current_section['title'],
                        'start': current_section['start'],
                        'end': current_section['end'],
                        'text': '\n'.join(current_text).strip()
                    })

                current_section = {
                    'title': section_match.group(1),
                    'start': self._time_to_seconds(section_match.group(2)),
                    'end': self._time_to_seconds(section_match.group(3))
                }
                current_text = []
            elif current_section and not line.startswith('#'):
                # Clean up the text
                clean_line = re.sub(r'\*\*\[.*?\]\*\*', '', line)  # Remove [B-ROLL] etc
                clean_line = re.sub(r'\*\*', '', clean_line)  # Remove bold markers
                clean_line = clean_line.strip()
                if clean_line and not clean_line.startswith('-'):
                    current_text.append(clean_line)

        # Add last section
        if current_section:
            sections.append({
                'title': current_section['title'],
                'start': current_section['start'],
                'end': current_section['end'],
                'text': '\n'.join(current_text).strip()
            })

        return sections

    def _time_to_seconds(self, time_str):
        """Convert MM:SS to seconds"""
        parts = time_str.split(':')
        return int(parts[0]) * 60 + int(parts[1])

    def create_text_image(self, text, filename, bg_color="0x1a1a2e", text_color="white",
                          font_size=48, padding=60):
        """Create an image with text overlay using FFmpeg"""
        # Escape special characters for FFmpeg
        escaped_text = text.replace("'", "'\\''").replace(":", "\\:")
        escaped_text = escaped_text[:200] + "..." if len(escaped_text) > 200 else escaped_text

        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c={bg_color}:s={self.width}x{self.height}:d=1',
            '-vf', f"drawtext=fontfile='{self.font}':text='{escaped_text}':fontcolor={text_color}:fontsize={font_size}:x=(w-text_w)/2:y=(h-text_h)/2:line_spacing=20",
            '-frames:v', '1',
            filename
        ]

        subprocess.run(cmd, capture_output=True)
        return filename

    def create_title_card(self, title, duration=3, output_file=None):
        """Create an animated title card"""
        if output_file is None:
            output_file = os.path.join(self.temp_dir, "title.mp4")

        escaped_title = title.replace("'", "'\\''").replace(":", "\\:")

        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c=0x1a1a2e:s={self.width}x{self.height}:d={duration}:r={self.fps}',
            '-vf', (
                f"drawtext=fontfile='{self.font}':"
                f"text='{escaped_title}':"
                f"fontcolor=white:fontsize=72:"
                f"x=(w-text_w)/2:y=(h-text_h)/2:"
                f"alpha='if(lt(t,0.5),t*2,if(lt(t,{duration-0.5}),1,({duration}-t)*2))'"
            ),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-r', str(self.fps),
            '-t', str(duration),
            '-pix_fmt', 'yuv420p',
            output_file
        ]

        subprocess.run(cmd, capture_output=True)
        return output_file

    def create_section_video(self, section, bg_image=None, output_file=None):
        """Create a video section with text overlay"""
        if output_file is None:
            output_file = os.path.join(self.temp_dir, f"section_{section['title'].replace(' ', '_')}.mp4")

        duration = section['end'] - section['start']

        # Get the speaking text (first quoted text or clean text)
        text = section.get('text', '')
        # Extract quoted text (actual speech)
        quotes = re.findall(r'"([^"]+)"', text)
        display_text = quotes[0][:150] if quotes else section['title']

        escaped_text = display_text.replace("'", "'\\''").replace(":", "\\:").replace("\n", " ")

        # Background
        if bg_image and os.path.exists(bg_image):
            input_args = ['-loop', '1', '-i', bg_image]
        else:
            input_args = ['-f', 'lavfi', '-i', f'color=c=0x0f0f23:s={self.width}x{self.height}:d={duration}']

        cmd = [
            'ffmpeg', '-y',
            *input_args,
            '-vf', (
                f"scale={self.width}:{self.height}:force_original_aspect_ratio=decrease,"
                f"pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2:color=0x0f0f23,"
                f"drawtext=fontfile='{self.font}':"
                f"text='{escaped_text}':"
                f"fontcolor=white:fontsize=42:"
                f"x=(w-text_w)/2:y=h-100-text_h:"
                f"box=1:boxcolor=black@0.7:boxborderw=20"
            ),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-r', str(self.fps),
            '-t', str(duration),
            '-pix_fmt', 'yuv420p',
            output_file
        ]

        subprocess.run(cmd, capture_output=True)
        return output_file

    def concatenate_videos(self, video_files, output_file):
        """Concatenate multiple videos into one"""
        # Create concat file
        concat_file = os.path.join(self.temp_dir, "concat.txt")
        with open(concat_file, 'w') as f:
            for video in video_files:
                f.write(f"file '{video}'\n")

        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-r', str(self.fps),
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            output_file
        ]

        subprocess.run(cmd, capture_output=True)
        return output_file

    def add_audio(self, video_file, audio_file, output_file):
        """Add audio track to video"""
        cmd = [
            'ffmpeg', '-y',
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            output_file
        ]

        subprocess.run(cmd, capture_output=True)
        return output_file

    def generate_from_script(self, script_path, output_name="video.mp4"):
        """Generate a complete video from a script file"""
        print(f"Parsing script: {script_path}")
        sections = self.parse_script(script_path)

        video_parts = []

        # Get title from first line
        with open(script_path, 'r') as f:
            title = f.readline().strip().replace('#', '').strip()

        # Create title card
        print(f"Creating title card: {title}")
        title_video = self.create_title_card(title[:60], duration=4)
        video_parts.append(title_video)

        # Create section videos
        for i, section in enumerate(sections):
            print(f"Creating section {i+1}/{len(sections)}: {section['title']}")
            section_video = self.create_section_video(section)
            video_parts.append(section_video)

        # Concatenate all parts
        output_path = self.output_dir / output_name
        print(f"Concatenating {len(video_parts)} parts...")
        self.concatenate_videos(video_parts, str(output_path))

        print(f"Video created: {output_path}")
        return str(output_path)


def create_demo_video():
    """Create a demo video to test the generator"""
    generator = FFmpegVideoGenerator(
        output_dir="/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/test-outputs"
    )

    script_path = "/Users/jumaanebey/Documents/stop-foreclosure-fast/youtube-scripts/01-stop-foreclosure-california.md"

    if os.path.exists(script_path):
        output = generator.generate_from_script(script_path, "ffmpeg-test-foreclosure.mp4")
        print(f"\nDemo video created: {output}")
        return output
    else:
        print("Script file not found!")
        return None


if __name__ == "__main__":
    create_demo_video()
