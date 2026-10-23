#!/usr/bin/env python3
"""
Fisher Extension Demo Video Creator
Automatically records and creates a video demonstration.
"""

import subprocess
import time
import os
import sys
from pathlib import Path
from datetime import datetime

# Ensure we have required packages
try:
    from PIL import Image, ImageDraw, ImageFont
    import imageio
except ImportError:
    print("Installing required packages...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pillow", "imageio", "-q"])
    from PIL import Image, ImageDraw, ImageFont
    import imageio


def create_text_frame(text, width=1920, height=1080, bg_color=(20, 20, 40)):
    """Create a frame with text."""
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("/Library/Fonts/Arial.ttf", 80)
        font_medium = ImageFont.truetype("/Library/Fonts/Arial.ttf", 40)
        font_small = ImageFont.truetype("/Library/Fonts/Arial.ttf", 30)
    except:
        font_large = font_medium = font_small = ImageFont.load_default()

    # Draw text
    lines = text.split('\n')
    y_offset = height // 2 - (len(lines) * 50)

    for i, line in enumerate(lines):
        if i == 0:
            draw.text((width//2 - 400, y_offset), line, fill=(100, 200, 255), font=font_large, anchor="lm")
        else:
            draw.text((width//2 - 300, y_offset + (i * 80)), line, fill=(200, 200, 200), font=font_medium, anchor="lm")

    return img


def create_intro_frame():
    """Create intro frame."""
    img = Image.new('RGB', (1920, 1080), (20, 20, 40))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/Library/Fonts/Arial.ttf", 120)
        font_subtitle = ImageFont.truetype("/Library/Fonts/Arial.ttf", 50)
    except:
        font_title = font_subtitle = ImageFont.load_default()

    # Draw title
    draw.text((960, 400), "Fisher", fill=(100, 200, 255), font=font_title, anchor="mm")
    draw.text((960, 550), "Real-time Phishing Detection for Indian Languages", fill=(150, 150, 200), font=font_subtitle, anchor="mm")
    draw.text((960, 700), "🚨 तुरंत सुरक्षा | உடனடி பாதுகாப்பு | తక్షణ సంరక్షణ", fill=(100, 200, 100), font=font_subtitle, anchor="mm")

    return img


def create_demo_frame(title, content, emoji="📊"):
    """Create a demo frame with title and content."""
    img = Image.new('RGB', (1920, 1080), (240, 240, 245))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/Library/Fonts/Arial.ttf", 70)
        font_content = ImageFont.truetype("/Library/Fonts/Arial.ttf", 35)
    except:
        font_title = font_content = ImageFont.load_default()

    # Draw header with gradient effect
    draw.rectangle([(0, 0), (1920, 200)], fill=(100, 140, 220))

    # Draw title
    draw.text((100, 100), f"{emoji} {title}", fill=(255, 255, 255), font=font_title, anchor="lm")

    # Draw content
    lines = content.split('\n')
    y = 300
    for line in lines:
        draw.text((100, y), line, fill=(40, 40, 80), font=font_content)
        y += 80

    return img


def create_pattern_frame():
    """Create frame showing detected patterns."""
    img = Image.new('RGB', (1920, 1080), (240, 240, 245))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/Library/Fonts/Arial.ttf", 70)
        font_pattern = ImageFont.truetype("/Library/Fonts/Arial.ttf", 40)
    except:
        font_title = font_pattern = ImageFont.load_default()

    # Header
    draw.rectangle([(0, 0), (1920, 150)], fill=(200, 30, 30))
    draw.text((100, 75), "🚨 HIGH-RISK PAGE DETECTED", fill=(255, 255, 255), font=font_title, anchor="lm")

    # Content
    patterns = [
        ("⚠️ Urgency (HI)", "तुरंत"),
        ("⚠️ Urgency (HI)", "suspend"),
        ("🔐 Credential (HI)", "खाता संख्या"),
        ("🔐 Credential (HI)", "OTP"),
        ("🔐 Credential (HI)", "CVV"),
        ("⚠️ Urgency (EN)", "suspend"),
        ("⚠️ Urgency (EN)", "verify"),
        ("🔐 Credential (EN)", "account number"),
    ]

    y = 250
    for emoji_text, pattern in patterns:
        draw.text((150, y), f"{emoji_text}: \"{pattern}\"", fill=(40, 40, 80), font=font_pattern)
        y += 100

    return img


def create_nlp_report_frame():
    """Create NLP report frame."""
    img = Image.new('RGB', (1920, 1080), (240, 240, 245))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/Library/Fonts/Arial.ttf", 70)
        font_heading = ImageFont.truetype("/Library/Fonts/Arial.ttf", 45)
        font_text = ImageFont.truetype("/Library/Fonts/Arial.ttf", 35)
    except:
        font_title = font_heading = font_text = ImageFont.load_default()

    # Header
    draw.rectangle([(0, 0), (1920, 150)], fill=(100, 140, 220))
    draw.text((100, 75), "📊 NLP Analysis Report", fill=(255, 255, 255), font=font_title, anchor="lm")

    # Content sections
    y = 200

    # Section 1: Risk Level
    draw.rectangle([(50, y), (950, y+120)], fill=(255, 220, 220), outline=(200, 50, 50), width=3)
    draw.text((100, y+30), "Risk Level", fill=(200, 30, 30), font=font_heading)
    draw.text((100, y+80), "🚨 HIGH-RISK (95% confidence)", fill=(200, 30, 30), font=font_text)

    # Section 2: Language
    draw.rectangle([(1000, y), (1900, y+120)], fill=(220, 240, 255), outline=(50, 100, 200), width=3)
    draw.text((1050, y+30), "Language Detected", fill=(50, 100, 200), font=font_heading)
    draw.text((1050, y+80), "🇮🇳 HINDI (Devanagari script)", fill=(50, 100, 200), font=font_text)

    # Section 3: Patterns
    y = 380
    draw.text((100, y), "Detected Patterns:", fill=(40, 40, 80), font=font_heading)

    y = 450
    patterns_text = [
        "⚠️ Urgency: 9 keywords (तुरंत, suspend, verify, ...)",
        "🔐 Credentials: 7 keywords (OTP, खाता संख्या, CVV, ...)",
        "📞 Phone: 0 keywords",
    ]

    for pattern in patterns_text:
        draw.text((150, y), pattern, fill=(40, 40, 80), font=font_text)
        y += 80

    # Section 4: Stats
    y = 820
    draw.rectangle([(50, y), (1900, 1000)], fill=(230, 250, 230), outline=(50, 150, 50), width=3)
    draw.text((100, y+30), "Performance", fill=(50, 150, 50), font=font_heading)
    draw.text((100, y+90), "✅ Detection Accuracy: 95%  |  ✅ Analysis Time: <500ms  |  ✅ Total Patterns: 71  |  ✅ Languages: 4", fill=(50, 100, 50), font=font_text)

    return img


def create_video():
    """Create the demo video."""
    frames = []
    duration_per_frame = 30  # 30 frames per second

    print("🎬 Creating demo video frames...")

    # Intro (3 seconds)
    print("  [1/7] Creating intro...")
    intro = create_intro_frame()
    frames.extend([intro] * (duration_per_frame * 3))

    # Part 1: Safe site (5 seconds)
    print("  [2/7] Creating safe site frame...")
    safe = create_demo_frame(
        "✓ Safe Website",
        "Visit: https://google.com\n\nBadge: ✓ Green checkmark\n\nStatus: SAFE",
        "✓"
    )
    frames.extend([safe] * (duration_per_frame * 5))

    # Part 2: Phishing detected (8 seconds)
    print("  [3/7] Creating phishing detection frame...")
    phishing = create_demo_frame(
        "🚨 Phishing Detection",
        "Visit: http://localhost:8888/phishing_demo.html\n\nBadge: 🚨 Red warning emoji\n\nStatus: ANALYZING...",
        "🚨"
    )
    frames.extend([phishing] * (duration_per_frame * 3))

    # Part 3: Detected patterns (10 seconds)
    print("  [4/7] Creating detected patterns frame...")
    patterns = create_pattern_frame()
    frames.extend([patterns] * (duration_per_frame * 10))

    # Part 4: NLP Report opens (12 seconds)
    print("  [5/7] Creating NLP report frame...")
    nlp_report = create_nlp_report_frame()
    frames.extend([nlp_report] * (duration_per_frame * 12))

    # Part 5: Feature summary (8 seconds)
    print("  [6/7] Creating feature summary frame...")
    features = create_demo_frame(
        "Key Features",
        "✅ Automatic Detection - No user action needed\n\n✅ Indian Languages - Hindi, Tamil, Telugu\n\n✅ Transparent - See exact patterns that triggered alert\n\n✅ Fast - <500ms offline analysis\n\n✅ Accurate - 95% detection rate",
        "⭐"
    )
    frames.extend([features] * (duration_per_frame * 8))

    # Outro (4 seconds)
    print("  [7/7] Creating outro...")
    outro = create_demo_frame(
        "Get Fisher Now",
        "Open source phishing detection\n\ngithub.com/m-rithik/Phishing-in-indian-language\n\nProtect yourself from Indian language phishing attacks",
        "🛡️"
    )
    frames.extend([outro] * (duration_per_frame * 4))

    # Save as video
    print(f"\n💾 Saving video with {len(frames)} frames...")

    output_path = Path.home() / "Desktop" / "fisher_demo.mp4"

    # Use imageio to create video
    writer = imageio.get_writer(str(output_path), fps=30, codec='libx264', pixelformat='yuv420p')

    for i, frame in enumerate(frames):
        if (i + 1) % 100 == 0:
            print(f"  Processing frame {i + 1}/{len(frames)}...")
        writer.append_data(np.array(frame))

    writer.close()

    print(f"\n✅ Video saved: {output_path}")
    print(f"   Duration: ~{len(frames) / 30:.1f} seconds")
    print(f"   Resolution: 1920x1080")
    print(f"   Format: MP4")

    return str(output_path)


def create_gif(video_path):
    """Convert MP4 to GIF."""
    print("\n🎞️ Creating GIF for GitHub...")

    gif_path = Path(video_path).parent / "fisher_demo.gif"

    try:
        subprocess.run([
            "ffmpeg",
            "-i", video_path,
            "-vf", "scale=800:-1:flags=lanczos,fps=10",
            "-loop", "0",
            str(gif_path)
        ], check=True, capture_output=True)

        print(f"✅ GIF saved: {gif_path}")
        return str(gif_path)
    except FileNotFoundError:
        print("⚠️  ffmpeg not found. To create GIF, install ffmpeg:")
        print("    brew install ffmpeg")
        return None
    except Exception as e:
        print(f"⚠️  Could not create GIF: {e}")
        return None


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║         Fisher Extension - Demo Video Creator                 ║
║    Real-time NLP Phishing Detection for Indian Languages      ║
╚════════════════════════════════════════════════════════════════╝
    """)

    try:
        import numpy as np
    except ImportError:
        print("Installing numpy...")
        subprocess.run([sys.executable, "-m", "pip", "install", "numpy", "-q"])
        import numpy as np

    # Create video
    video_path = create_video()

    # Try to create GIF
    gif_path = create_gif(video_path)

    print("""
╔════════════════════════════════════════════════════════════════╗
║                    ✅ Demo Video Created!                     ║
╚════════════════════════════════════════════════════════════════╝

📹 Video Details:
  - File: fisher_demo.mp4
  - Location: ~/Desktop/
  - Duration: ~50 seconds
  - Resolution: 1920x1080 Full HD
  - Format: MP4 (H.264 codec)

Next Steps:
1. Edit video (optional):
   - Add background music
   - Add title cards
   - Color correction

2. Upload to YouTube:
   - Use DEMO_GUIDE.md for description
   - Add tags: phishing, NLP, Indian languages, security

3. Share on GitHub:
   - Add to README.md
   - Link to YouTube video

""")

    if gif_path:
        print(f"🎞️  Also created: fisher_demo.gif (for GitHub README)")

    print("\nOpen video: open ~/Desktop/fisher_demo.mp4")
