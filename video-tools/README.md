# Video Tools

Video generation system for the My Foreclosure Solution marketing campaign. Creates faceless videos with AI voiceover for YouTube, TikTok, Instagram, and other social media platforms.

## Overview

This folder contains Python scripts that use FFmpeg and Edge TTS to generate marketing videos automatically from scripts. The system supports multiple output formats:

- **Horizontal (1920x1080)** - YouTube, Facebook
- **Vertical (1080x1920)** - TikTok, Instagram Reels, YouTube Shorts

All tools are free and produce watermark-free output.

---

## Scripts

### Core Video Generators

| Script | Description |
|--------|-------------|
| `ffmpeg_video_generator.py` | Base FFmpeg generator - parses YouTube scripts and creates videos with text overlays |
| `simple_video_gen.py` | Simplified version for quick video generation from script files |
| `video_with_voice.py` | Adds AI voiceover using Edge TTS (free Microsoft voices) |
| `video_with_voice_v2.py` | Improved voice generator with better timing |

### Style-Specific Generators

| Script | Description |
|--------|-------------|
| `video_whiteboard.py` | Whiteboard-style videos with left-to-right reveal animation |
| `video_whiteboard_test.py` | Test version of whiteboard generator |
| `video_scribe_style.py` | VideoScribe-style drawing hand animation effect |
| `video_with_visuals.py` | Videos with background images and visual elements |
| `video_pro_v2.py` | Professional generator with dynamic animations and transitions |
| `video_engaging.py` | High-engagement version with zoom effects and sound effects |
| `video_final.py` | Final production-ready generator |
| `video_scripts_extra.py` | Additional script processing utilities |
| `video_generator_pro.py` | Advanced generator with color themes and effects |

### Utilities

| Script | Description |
|--------|-------------|
| `add_captions.py` | Burns captions into videos with branding overlay |
| `capcut_draft_creator.py` | Creates CapCut project files for manual editing |

---

## Final Videos

Location: `final-videos/`

| Video | Duration | Size | Platform |
|-------|----------|------|----------|
| `stop-foreclosure-visual.mp4` | ~1 min | 5.7 MB | YouTube |
| `stop-foreclosure-scribe.mp4` | ~73 sec | 3.4 MB | YouTube |
| `stop-foreclosure-whiteboard.mp4` | ~1 min | 2.8 MB | YouTube |
| `stop-foreclosure-short.mp4` | ~49 sec | 2.2 MB | TikTok, Reels |
| `stop-foreclosure.mp4` | ~1 min | 716 KB | YouTube |
| `5-mistakes-visual.mp4` | ~1 min | 5.3 MB | YouTube |
| `5-mistakes-scribe.mp4` | ~71 sec | 3.9 MB | YouTube |
| `5-mistakes-whiteboard.mp4` | ~1 min | 2.7 MB | YouTube |
| `5-mistakes-short.mp4` | ~47 sec | 2.8 MB | TikTok, Reels |
| `5-mistakes.mp4` | ~1 min | 628 KB | YouTube |
| `california-timeline.mp4` | ~1 min | 636 KB | YouTube |
| `los-angeles.mp4` | ~30 sec | 512 KB | Local SEO |
| `san-diego.mp4` | ~30 sec | 532 KB | Local SEO |
| `sell-foreclosure.mp4` | ~30 sec | 536 KB | YouTube |

---

## Captioned Videos

Location: `captioned/`

Videos with burned-in captions and branding overlay ("MyForeclosureSolution.com | (949) 565-5285"):

- FAQ videos (how long, hurt credit, keep home, stop auction)
- City-specific videos (LA, San Diego, Sacramento, etc.)
- Educational content (notice of default, short sale guide, etc.)

---

## Test Outputs

Location: `test-outputs/`

Contains intermediate outputs and both horizontal + vertical versions of videos. Files ending in `-VERTICAL.mp4` are formatted for TikTok/Reels (1080x1920).

**Debug/Test Files** (can be excluded from production):
- `debug-test.mp4` - Debug output
- `simple-test.mp4` - Simple test render
- `first3sec.mp4` - First 3 seconds test
- `ffmpeg-test-foreclosure.mp4` - FFmpeg test output
- `ffmpeg-test-v2.mp4` - FFmpeg v2 test
- `foreclosure-video-v3.mp4` - Development version
- `foreclosure-WITH-VOICE.mp4` - Voice test

---

## Supporting Files

| File | Description |
|------|-------------|
| `VIDEO_TOOLS_COMPARISON.md` | Comparison of video creation tools and recommendations |
| `CLAUDE-CHROME-INSTRUCTIONS.md` | Deployment checklist for social media platforms |
| `notebooklm-content.md` | Content for NotebookLM podcast generation |

### Directories

| Directory | Description |
|-----------|-------------|
| `CapCutAPI/` | Third-party library for CapCut automation |
| `antigravity-assets/` | Prompts for AI image generation (whiteboard visuals) |
| `venv/` | Python virtual environment |
| `__pycache__/` | Python bytecode cache |

---

## Usage

### Prerequisites

```bash
# FFmpeg (required)
brew install ffmpeg

# Edge TTS (for AI voice)
pip install edge-tts

# Activate virtual environment (optional)
source venv/bin/activate
```

### Generate a Video

```bash
# Basic video from script
python3 simple_video_gen.py

# Video with AI voiceover
python3 video_with_voice.py

# Whiteboard style
python3 video_whiteboard.py

# Add captions to existing videos
python3 add_captions.py
```

### Voice Options (Edge TTS)

All voices are free with no limits:
- `en-US-AndrewNeural` - Warm, confident (recommended)
- `en-US-GuyNeural` - Energetic, passionate
- `en-US-BrianNeural` - Approachable, casual
- `en-US-ChristopherNeural` - Reliable, authoritative

---

## File Size Note

The video files in this directory total approximately **167 MB**:
- `final-videos/` - ~32 MB
- `captioned/` - ~15 MB
- `test-outputs/` - ~73 MB
- Total directory with all files: ~214 MB

Consider adding large video files to `.gitignore` or using Git LFS for version control.

---

## Workflow Recommendation

1. **Quick Start**: Use CapCut Desktop manually with templates
2. **Batch Generation**: Use `video_with_voice.py` for automated production
3. **Final Polish**: Import FFmpeg output into CapCut for finishing touches

See `VIDEO_TOOLS_COMPARISON.md` for detailed recommendations.
