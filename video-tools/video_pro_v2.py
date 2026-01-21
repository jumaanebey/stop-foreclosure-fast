#!/usr/bin/env python3
"""
ENGAGING Video Generator - High Quality, Entertaining Content
Features: Dynamic animations, transitions, sound effects, visual variety
"""
import subprocess
import os
import tempfile
import random
import math

OUTPUT_DIR = "/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/final-videos"
VOICE = "en-US-GuyNeural"  # More energetic voice
VOICE_RATE = "+5%"  # Slightly faster, more dynamic

# Color palette - vibrant and professional
COLORS = {
    "primary": "FF6B35",      # Orange
    "secondary": "1E3A5F",    # Deep blue
    "accent": "00D4AA",       # Teal
    "dark": "0D1B2A",         # Near black
    "light": "E8F1F8",        # Light blue-white
    "warning": "FFB800",      # Gold/yellow
    "success": "00C853",      # Green
}

WIDTH = 1920
HEIGHT = 1080

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_voice(text, output_path):
    cmd = ["edge-tts", "--voice", VOICE, "--rate", VOICE_RATE, "--text", text, "--write-media", output_path]
    subprocess.run(cmd, capture_output=True)
    return os.path.exists(output_path)

def get_duration(path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 5.0

def create_whoosh_sound(output_path, duration=0.3):
    """Create a subtle whoosh transition sound"""
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"sine=frequency=800:duration={duration}",
        "-af", f"volume=0.1,afade=t=in:d=0.05,afade=t=out:st={duration-0.1}:d=0.1,lowpass=f=2000",
        "-c:a", "libmp3lame", output_path
    ]
    subprocess.run(cmd, capture_output=True)

def create_hook_intro(title, temp_dir):
    """Create attention-grabbing hook intro (first 3 seconds)"""
    audio_path = f"{temp_dir}/hook.mp3"
    video_path = f"{temp_dir}/hook.mp4"

    # Punchy hook text
    hooks = [
        "STOP! Watch this before you lose your home",
        "What your bank doesnt want you to know",
        "This could save your house",
        "Foreclosure? You have MORE options than you think",
        "WAIT - dont make this mistake",
    ]
    hook = random.choice(hooks)

    generate_voice(hook, audio_path)
    duration = get_duration(audio_path) + 0.5

    # Animated background with zoom effect
    filter_complex = f"""
    color=c=0x{COLORS['dark']}:s={WIDTH}x{HEIGHT}:d={duration},
    drawbox=x=0:y=0:w=iw:h=ih:color=0x{COLORS['primary']}@0.1:t=fill,
    zoompan=z='min(zoom+0.002,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duration*30)}:s={WIDTH}x{HEIGHT}:fps=30,
    drawtext=text='{hook.upper()}':fontsize=72:fontcolor=white:x='(w-text_w)/2':y='(h-text_h)/2':
        shadowcolor=black:shadowx=3:shadowy=3,
    drawbox=x=0:y=ih-8:w='iw*t/{duration}':h=8:color=0x{COLORS['primary']}:t=fill
    """.replace('\n', '')

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", filter_complex,
        "-i", audio_path,
        "-c:v", "libx264", "-c:a", "aac",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-shortest",
        video_path
    ]
    subprocess.run(cmd, capture_output=True)
    return video_path if os.path.exists(video_path) else None

def create_title_card(title, subtitle, temp_dir):
    """Create dynamic animated title card"""
    audio_path = f"{temp_dir}/title.mp3"
    video_path = f"{temp_dir}/title.mp4"

    text = f"{title}"
    generate_voice(text, audio_path)
    duration = max(get_duration(audio_path), 3) + 1

    title_clean = title.replace("'", "").replace(":", " -").upper()

    # Gradient background with animated elements
    filter_complex = f"""
    color=c=0x{COLORS['secondary']}:s={WIDTH}x{HEIGHT}:d={duration},
    drawbox=x=0:y=0:w=iw:h=ih:color=0x{COLORS['dark']}@0.7:t=fill,
    drawbox=x=-200+t*100:y=100:w=400:h=200:color=0x{COLORS['primary']}@0.15:t=fill,
    drawbox=x=iw-t*80:y=ih-300:w=300:h=300:color=0x{COLORS['accent']}@0.1:t=fill,
    drawtext=text='{title_clean}':fontsize=80:fontcolor=white:
        x='(w-text_w)/2':y='(h-text_h)/2-60':
        shadowcolor=0x{COLORS['primary']}:shadowx=4:shadowy=4,
    drawtext=text='MyForeclosureSolution.com':fontsize=36:fontcolor=0x{COLORS['accent']}:
        x='(w-text_w)/2':y='(h-text_h)/2+80',
    drawbox=x=(iw-600)/2:y=ih/2+140:w=600:h=4:color=0x{COLORS['primary']}:t=fill
    """.replace('\n', '')

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", filter_complex,
        "-i", audio_path,
        "-c:v", "libx264", "-c:a", "aac",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-shortest",
        video_path
    ]
    subprocess.run(cmd, capture_output=True)
    return video_path if os.path.exists(video_path) else None

def create_section_video(title, points, dialogue, section_num, total, section_type, temp_dir):
    """Create visually engaging section with animations"""
    audio_path = f"{temp_dir}/s{section_num}.mp3"
    video_path = f"{temp_dir}/s{section_num}.mp4"

    if not generate_voice(dialogue, audio_path):
        return None

    duration = get_duration(audio_path) + 0.5

    title_clean = title.replace("'", "").replace(":", " -")

    # Color scheme based on section type
    if "option" in title.lower() or "sign" in title.lower():
        bg_color = COLORS['secondary']
        accent = COLORS['primary']
    elif "tip" in title.lower() or "help" in title.lower():
        bg_color = COLORS['dark']
        accent = COLORS['success']
    else:
        bg_color = COLORS['dark']
        accent = COLORS['accent']

    # Build points with bullet animations
    points_filter = ""
    if points:
        y_start = 380
        for i, p in enumerate(points[:4]):
            p_clean = p.replace("'", "")[:45]
            delay = 0.3 + (i * 0.4)  # Stagger appearance
            # Fade in each bullet point
            points_filter += f",drawtext=text='» {p_clean}':fontsize=40:fontcolor=white@'if(gt(t,{delay}),min((t-{delay})*3,1),0)':x=180:y={y_start + i*70}"

    # Progress indicator
    progress = section_num / total

    # Main filter with animated elements
    filter_complex = f"""
    color=c=0x{bg_color}:s={WIDTH}x{HEIGHT}:d={duration},
    drawbox=x=0:y=0:w=iw:h=ih:color=0x{COLORS['dark']}@0.3:t=fill,
    drawbox=x='mod(t*50,iw+400)-400':y=50:w=200:h=100:color=0x{accent}@0.08:t=fill,
    drawbox=x='iw-mod(t*30,iw+300)':y=ih-200:w=150:h=150:color=0x{COLORS['primary']}@0.06:t=fill,
    drawbox=x=0:y=0:w=12:h=ih:color=0x{accent}:t=fill,
    drawtext=text='{section_num}':fontsize=120:fontcolor=0x{accent}:x=60:y=60,
    drawtext=text='of {total}':fontsize=32:fontcolor=white@0.6:x=80:y=180,
    drawtext=text='{title_clean}':fontsize=58:fontcolor=white:x=180:y=250:
        shadowcolor=black:shadowx=2:shadowy=2,
    drawbox=x=100:y=ih-50:w={int(1720*progress)}:h=6:color=0x{accent}:t=fill,
    drawbox=x=100:y=ih-50:w=1720:h=6:color=white@0.2:t=fill{points_filter}
    """.replace('\n', '')

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", filter_complex,
        "-i", audio_path,
        "-c:v", "libx264", "-c:a", "aac",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-shortest",
        video_path
    ]
    subprocess.run(cmd, capture_output=True)
    return video_path if os.path.exists(video_path) else None

def create_cta_card(temp_dir):
    """Create compelling call-to-action end card"""
    audio_path = f"{temp_dir}/cta.mp3"
    video_path = f"{temp_dir}/cta.mp4"

    cta_text = "Ready to save your home? Call us now for your FREE consultation. We've helped hundreds of California homeowners just like you. The call is free, and it could change everything."
    generate_voice(cta_text, audio_path)
    duration = get_duration(audio_path) + 3

    filter_complex = f"""
    color=c=0x{COLORS['primary']}:s={WIDTH}x{HEIGHT}:d={duration},
    drawbox=x=0:y=0:w=iw:h=ih:color=0x{COLORS['dark']}@0.85:t=fill,
    drawbox=x='iw/2-400':y='ih/2-80':w=800:h=160:color=0x{COLORS['primary']}:t=fill,
    drawtext=text='CALL NOW':fontsize=72:fontcolor=white:
        x='(w-text_w)/2':y='(h-text_h)/2-20',
    drawtext=text='(949) 565-5285':fontsize=64:fontcolor=white:
        x='(w-text_w)/2':y='(h-text_h)/2+120',
    drawtext=text='MyForeclosureSolution.com':fontsize=42:fontcolor=0x{COLORS['accent']}:
        x='(w-text_w)/2':y='(h-text_h)/2+220',
    drawtext=text='FREE CONSULTATION - NO OBLIGATION':fontsize=28:fontcolor=white@0.8:
        x='(w-text_w)/2':y=ih-100,
    drawbox=x=0:y=ih-10:w='iw*t/{duration}':h=10:color=0x{COLORS['accent']}:t=fill
    """.replace('\n', '')

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", filter_complex,
        "-i", audio_path,
        "-c:v", "libx264", "-c:a", "aac",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-shortest",
        video_path
    ]
    subprocess.run(cmd, capture_output=True)
    return video_path if os.path.exists(video_path) else None

def create_subscribe_end(temp_dir):
    """Create YouTube subscribe end screen"""
    video_path = f"{temp_dir}/subscribe.mp4"
    duration = 5

    filter_complex = f"""
    color=c=0x{COLORS['dark']}:s={WIDTH}x{HEIGHT}:d={duration},
    drawbox=x='iw/2-150':y='ih/2-150':w=300:h=300:color=0xFF0000:t=fill,
    drawtext=text='SUBSCRIBE':fontsize=48:fontcolor=white:
        x='(w-text_w)/2':y='(h-text_h)/2-20',
    drawtext=text='for more tips':fontsize=32:fontcolor=white@0.8:
        x='(w-text_w)/2':y='(h-text_h)/2+40',
    drawtext=text='Like & Share if this helped you!':fontsize=36:fontcolor=0x{COLORS['accent']}:
        x='(w-text_w)/2':y=ih-150
    """.replace('\n', '')

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", filter_complex,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-c:v", "libx264", "-c:a", "aac",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        video_path
    ]
    subprocess.run(cmd, capture_output=True)
    return video_path if os.path.exists(video_path) else None

def add_transitions_and_music(segments, output_path, temp_dir):
    """Combine segments with crossfade transitions and background music"""

    # First concat all segments
    concat_list = f"{temp_dir}/concat.txt"
    with open(concat_list, "w") as f:
        for seg in segments:
            f.write(f"file '{seg}'\n")

    concat_path = f"{temp_dir}/concat.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c:v", "libx264", "-c:a", "aac",
        concat_path
    ]
    subprocess.run(cmd, capture_output=True)

    if not os.path.exists(concat_path):
        return None

    # Get duration for music
    duration = get_duration(concat_path)

    # Create upbeat background music
    music_path = f"{temp_dir}/music.mp3"
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"sine=frequency=130:duration={duration+5}",
        "-af", (
            "volume=0.02,"
            "tremolo=f=2:d=0.3,"
            "lowpass=f=400,"
            "highpass=f=80,"
            f"afade=t=out:st={duration-4}:d=4"
        ),
        "-c:a", "libmp3lame",
        music_path
    ]
    subprocess.run(cmd, capture_output=True)

    # Mix music with video
    cmd = [
        "ffmpeg", "-y",
        "-i", concat_path,
        "-i", music_path,
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:weights=1 0.15[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac",
        output_path
    ]
    subprocess.run(cmd, capture_output=True)

    return output_path if os.path.exists(output_path) else None

def create_video(script, output_name):
    """Create complete engaging video"""
    ensure_dirs()

    title = script["title"]
    sections = script["sections"]

    print(f"\n🎬 Creating: {title}")

    with tempfile.TemporaryDirectory() as temp_dir:
        segments = []

        # 1. Attention-grabbing hook
        print("  → Creating hook...")
        hook = create_hook_intro(title, temp_dir)
        if hook:
            segments.append(hook)
            print(f"     ✓ Hook ({get_duration(hook):.1f}s)")

        # 2. Title card
        print("  → Creating title...")
        title_vid = create_title_card(title, "", temp_dir)
        if title_vid:
            segments.append(title_vid)
            print(f"     ✓ Title ({get_duration(title_vid):.1f}s)")

        # 3. Content sections
        total = len([s for s in sections if s.get("dialogue")])
        num = 0
        for section in sections:
            if not section.get("dialogue"):
                continue
            num += 1
            print(f"  → Section {num}/{total}: {section['title'][:30]}...")

            seg = create_section_video(
                section["title"],
                section.get("points", []),
                section["dialogue"],
                num, total,
                section.get("type", "info"),
                temp_dir
            )
            if seg:
                segments.append(seg)
                print(f"     ✓ {get_duration(seg):.1f}s")

        # 4. Call to action
        print("  → Creating CTA...")
        cta = create_cta_card(temp_dir)
        if cta:
            segments.append(cta)
            print(f"     ✓ CTA ({get_duration(cta):.1f}s)")

        # 5. Subscribe end screen
        print("  → Creating end screen...")
        end = create_subscribe_end(temp_dir)
        if end:
            segments.append(end)
            print(f"     ✓ End ({get_duration(end):.1f}s)")

        # 6. Combine with transitions and music
        print("  → Adding music & combining...")
        final_path = f"{OUTPUT_DIR}/{output_name}.mp4"
        result = add_transitions_and_music(segments, final_path, temp_dir)

        if result and os.path.exists(final_path):
            duration = get_duration(final_path)
            size = os.path.getsize(final_path) / (1024*1024)
            print(f"\n✅ {output_name}.mp4 ({duration/60:.1f} min, {size:.1f} MB)")
            return final_path

    return None

# ============================================================
# ENGAGING SCRIPTS - Written for retention
# ============================================================

SCRIPTS = {
    "stop-foreclosure-fast": {
        "title": "How to Stop Foreclosure FAST",
        "sections": [
            {
                "title": "You Have More Power Than You Think",
                "points": ["Banks dont want your house", "They lose money on foreclosure", "Theyd rather work with you"],
                "dialogue": "Heres something your bank will never tell you. They dont actually want to foreclose on your home. It costs them tens of thousands of dollars. They would much rather work something out with you. And thats your leverage.",
                "type": "hook"
            },
            {
                "title": "Option 1 - Loan Modification",
                "points": ["Lower your payment permanently", "Reduce interest rate", "Extend your loan term"],
                "dialogue": "Option one is a loan modification. This is where your bank rewrites your loan terms to make it affordable. Lower interest rate. Longer term. Lower payment. And heres the secret - banks approve these more often than you think. You just need to know how to ask.",
                "type": "option"
            },
            {
                "title": "Option 2 - Forbearance",
                "points": ["Pause payments temporarily", "Catch up over time", "Perfect for temporary hardship"],
                "dialogue": "Option two is forbearance. Lost your job? Medical emergency? This lets you pause or reduce payments while you get back on your feet. The key is acting fast and having a plan to catch up.",
                "type": "option"
            },
            {
                "title": "Option 3 - Sell and Keep Your Equity",
                "points": ["Cash offer in 24 hours", "Close in 7 days", "Walk away with money"],
                "dialogue": "Option three - and this is the one most people miss - is selling your home fast. Even in foreclosure, you likely have equity. That money belongs to you. Sell to a cash buyer, pay off the mortgage, and walk away with cash for your fresh start. Way better than losing everything at auction.",
                "type": "option"
            },
            {
                "title": "The California Advantage",
                "points": ["200 days to act", "Strong homeowner protections", "Multiple chances to save it"],
                "dialogue": "Heres good news if youre in California. You have about 200 days from your first missed payment to the auction. Thats over 6 months of runway. California has some of the strongest homeowner protections in the country. Use them.",
                "type": "tip"
            },
            {
                "title": "What Most People Do Wrong",
                "points": ["They ignore the mail", "They dont answer lender calls", "They wait too long"],
                "dialogue": "The biggest mistake I see? People bury their head in the sand. They ignore the letters. They dont answer when the bank calls. And by the time they take action, theyve lost most of their options. Dont be that person.",
                "type": "warning"
            },
            {
                "title": "Your Next Step",
                "points": ["Free consultation", "Know all your options", "Take action today"],
                "dialogue": "Heres what I want you to do right now. Pick up the phone and call us for a free consultation. Well review your specific situation and tell you exactly what options you have. No pressure. No obligation. Just real answers.",
                "type": "cta"
            }
        ]
    },
    "5-biggest-mistakes": {
        "title": "5 Mistakes That Will Cost You Your Home",
        "sections": [
            {
                "title": "Mistake 1 - Ignoring the Problem",
                "points": ["Every day costs you options", "Banks start the clock immediately", "Silence helps no one"],
                "dialogue": "Mistake number one - ignoring the problem. I get it. Those letters are scary. But every day you ignore them, you lose options. The foreclosure clock starts ticking the moment you miss a payment. Your silence only helps the bank.",
                "type": "warning"
            },
            {
                "title": "Mistake 2 - Not Opening Your Mail",
                "points": ["Critical deadlines in those letters", "Legal notices require response", "Missing deadlines loses rights"],
                "dialogue": "Mistake number two - not opening your mail. Those certified letters contain critical deadlines. Notice of Default. Notice of Sale. Each one gives you less time to act. Miss a deadline, lose a right. Its that simple.",
                "type": "warning"
            },
            {
                "title": "Mistake 3 - Waiting for a Miracle",
                "points": ["Hope is not a strategy", "Your situation wont fix itself", "Action is the only answer"],
                "dialogue": "Mistake number three - waiting for a miracle. Hoping youll win the lottery. Waiting for a rich relative to save you. Listen - hope is not a strategy. Your situation will not fix itself. The only thing that works is taking action. Today.",
                "type": "warning"
            },
            {
                "title": "Mistake 4 - Hiring the Wrong Help",
                "points": ["Scammers target foreclosure victims", "Never pay upfront fees", "Verify credentials"],
                "dialogue": "Mistake number four - hiring the wrong help. Scammers specifically target people in foreclosure because theyre desperate. Never pay big upfront fees. Never sign over your deed. Always verify credentials. If something sounds too good to be true, run.",
                "type": "warning"
            },
            {
                "title": "Mistake 5 - Giving Up Too Early",
                "points": ["Options exist until auction day", "Many have saved their homes last minute", "Never assume its too late"],
                "dialogue": "Mistake number five - giving up too early. Ive seen people save their homes the week before auction. Options exist right up until that gavel falls. Never assume its too late. Make that call. Fight for your home.",
                "type": "warning"
            },
            {
                "title": "Theres Still Time",
                "points": ["Free consultation", "Real solutions", "Call now"],
                "dialogue": "If youre watching this, theres still time. You havent lost your home yet. Call us right now for a free consultation. Let us show you what options you still have. That call could save your home.",
                "type": "cta"
            }
        ]
    }
}

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 ENGAGING Video Generator v2")
    print("=" * 60)

    for key, script in SCRIPTS.items():
        create_video(script, key)

    print("\n" + "=" * 60)
    print("✅ All videos complete!")
    print(f"📁 {OUTPUT_DIR}")
    print("=" * 60)
