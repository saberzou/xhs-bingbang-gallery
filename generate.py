#!/usr/bin/env python3
"""
XHS Daily Content Generator for @BingBang
Generates a cute B&W doodle with English text + Chinese caption.
Output: drafts/YYYY-MM-DD/ with image.png, caption.md, metadata.json
"""

import json
import os
import random
import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
DRAFTS_DIR = SCRIPT_DIR / "drafts"
THEMES_FILE = SCRIPT_DIR / "themes" / "theme-bank.md"
NANO_BANANA = Path.home() / ".openclaw/workspace-axel/skills/nano-banana/generate_image.py"

# Content pillars — rotate by day of week
PILLARS = ["设计感悟", "生活碎片", "创意灵感", "文字涂鸦", "情绪速写", "设计感悟", "生活碎片"]

# Base prompt template for the new style
STYLE_PROMPT = """A cute, imperfect hand-drawn black and white marker sketch on a pure white background. 
Style: Looks like it was genuinely doodled in a sketchbook with a thick black Sharpie pen. Organic, slightly wobbly lines, charming imperfections, not perfectly straight or vector-like. Bold outlines and solid ink scribbled fills.
Must include exactly 4 floating 4-pointed diamond sparkle stars (✦) with hand-drawn, slightly uneven edges.
The objects should be clustered in the center, floating, not grounded. No background elements. No gray tones, strictly black and white ink.
Draw these specific objects: {objects}.
At the very bottom, centered in an imperfect, organic hand-lettered italic font, write exactly this text: "{text}"
"""

def parse_theme_bank():
    """Parse the new theme-bank.md format."""
    themes = {}
    current_pillar = None
    
    content = THEMES_FILE.read_text(encoding="utf-8")
    lines = content.split('\n')
    
    current_theme = {}
    
    for line in lines:
        if line.startswith('## '):
            # Extract pillar name before any parentheses
            pillar_match = re.match(r'## ([^\(]+)', line)
            if pillar_match:
                current_pillar = pillar_match.group(1).strip()
                themes[current_pillar] = []
        elif line.strip() and current_pillar:
            # Parse theme blocks
            if re.match(r'^\d+\.', line) or line.startswith('   '):
                line = line.strip()
                if line.startswith(str(len(themes[current_pillar])+1) + '.') or ('text:' in line and not current_theme):
                    if current_theme:
                        themes[current_pillar].append(current_theme)
                        current_theme = {}
                
                if 'text:' in line:
                    current_theme['text'] = line.split('text:')[1].strip().strip('"')
                elif 'objects:' in line:
                    current_theme['objects'] = line.split('objects:')[1].strip()
                elif 'caption:' in line:
                    current_theme['caption'] = line.split('caption:')[1].strip()
    
    # Don't forget the last theme
    if current_theme and current_pillar:
        themes[current_pillar].append(current_theme)
        
    return themes

# Core hashtags
CORE_TAGS = ["#手绘", "#涂鸦", "#黑白", "#极简", "#插画"]
PILLAR_TAGS = {
    "设计感悟": ["#设计师日常", "#设计灵感", "#设计思考"],
    "生活碎片": ["#生活感悟", "#日常", "#生活碎片"],
    "创意灵感": ["#创意", "#灵感", "#脑洞"],
    "文字涂鸦": ["#文字控", "#手写", "#英文字体"],
    "情绪速写": ["#情绪", "#打工人", "#日常心情"],
}

def pick_theme(themes_data, pillar: str) -> dict:
    """Pick a random theme from the given pillar."""
    themes = themes_data.get(pillar, themes_data.get("生活碎片", []))
    if not themes:
        # Fallback if parsing fails
        return {
            "text": "Keep going.",
            "objects": "a cute little coffee cup with a happy face",
            "caption": "继续前进吧。"
        }
    return random.choice(themes)

def generate_image(theme: dict, output_path: Path) -> bool:
    """Generate image using nano-banana."""
    prompt = STYLE_PROMPT.format(
        objects=theme.get("objects", "cute shapes"),
        text=theme.get("text", "")
    )

    try:
        result = subprocess.run(
            [
                "python3", str(NANO_BANANA),
                prompt,
                "--aspect-ratio", "1:1",
                "-o", str(output_path),
                "--json",
            ],
            capture_output=True, text=True, timeout=120,
        )
        data = json.loads(result.stdout)
        return data.get("status") == "success"
    except Exception as e:
        print(f"Image generation failed: {e}", file=sys.stderr)
        return False

def generate_caption(theme: dict, pillar: str) -> str:
    """Generate XHS caption from theme."""
    base_caption = theme.get("caption", "")

    # Pick hashtags
    tags = random.sample(CORE_TAGS, 3) + random.sample(PILLAR_TAGS.get(pillar, ["#涂鸦"]), 1)
    tags.append("#BingBang")
    tag_line = " ".join(tags)

    caption = f"{base_caption}\n\n{tag_line}"
    return caption

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    day_of_week = datetime.now().weekday()  # 0=Monday

    themes_data = parse_theme_bank()
    
    # Pick pillar based on day
    pillar = PILLARS[day_of_week]

    # Pick theme
    theme = pick_theme(themes_data, pillar)

    # Create output directory
    output_dir = DRAFTS_DIR / today
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📅 Date: {today}")
    print(f"🎯 Pillar: {pillar}")
    print(f"💡 Text: {theme.get('text')}")
    print(f"🎨 Objects: {theme.get('objects')}")
    print()

    # Generate image
    image_path = output_dir / "image.png"
    print("🎨 Generating image in new 1:1 cute sticker style...")
    success = generate_image(theme, image_path)
    if success:
        print(f"   ✅ Saved to {image_path}")
    else:
        print("   ❌ Image generation failed")

    # Generate caption
    caption = generate_caption(theme, pillar)

    caption_path = output_dir / "caption.md"
    caption_path.write_text(f"{caption}\n", encoding="utf-8")
    print(f"📝 Caption saved to {caption_path}")

    # Save metadata
    metadata = {
        "date": today,
        "pillar": pillar,
        "theme": theme,
        "image": str(image_path),
        "generated_at": datetime.now().isoformat(),
    }
    meta_path = output_dir / "metadata.json"
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📋 Metadata saved to {meta_path}")

    print()
    print("=" * 40)
    print(f"📄 Caption:\n{caption}")
    print("=" * 40)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
