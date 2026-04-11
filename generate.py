#!/usr/bin/env python3
"""
XHS Daily Content Generator for @BingBang (v2 — Dual Metaphor)
Generates TWO contrasting doodles per quote + Chinese caption.
Output: drafts/YYYY-MM-DD/ with image_a.png, image_b.png, caption.md, metadata.json
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

# Base prompt template
STYLE_PROMPT = """A minimalist hand-drawn doodle illustration in black ink on a pure white background. The style is indie-comic/bullet-journal kawaii-inspired with thick, uniform, slightly wobbly outlines (mimicking a felt-tip fineliner or marker). 
The subject is {objects}, anthropomorphized with a simple face consisting of two tiny dot eyes and a small curved smile (or closed downward 'v' eyes).
Use high-contrast solid black for small accents (like leaves, UI icons, or tiny pin-prick eyes) and hollow outlines for the rest.
Must include exactly 4 or 5 floating 4-pointed hollow diamond sparkles (✦) and tiny floating bubbles to fill negative space.
Centralized floating composition with heavy use of negative space. No background grounding lines.
At the very bottom, separated by a clear margin of white space, hand-lettered bold all-caps sans-serif typography with rounded terminals that reads exactly: "{text}"
"""

def parse_theme_bank():
    """Parse theme-bank.md format. Supports objects + objects_alt fields."""
    themes = {}
    current_pillar = None

    content = THEMES_FILE.read_text(encoding="utf-8")
    lines = content.split('\n')

    current_theme = {}

    for line in lines:
        if line.startswith('## '):
            pillar_match = re.match(r'## ([^\(]+)', line)
            if pillar_match:
                current_pillar = pillar_match.group(1).strip()
                themes[current_pillar] = []
        elif line.strip() and current_pillar:
            line = line.strip()
            if re.match(r'^\d+\.', line):
                if current_theme:
                    themes[current_pillar].append(current_theme)
                    current_theme = {}

            if 'text:' in line and 'objects' not in line:
                current_theme['text'] = line.split('text:')[1].strip().strip('"')
            elif 'objects_alt:' in line:
                current_theme['objects_alt'] = line.split('objects_alt:')[1].strip().strip('"')
            elif 'objects:' in line:
                current_theme['objects'] = line.split('objects:')[1].strip().strip('"')
            elif 'caption:' in line:
                current_theme['caption'] = line.split('caption:')[1].strip().strip('"')

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
        return {
            "text": "Keep going.",
            "objects": "a cute little coffee cup with a happy face",
            "objects_alt": "a tiny wind-up toy robot marching forward with determination",
            "caption": "继续前进吧。"
        }
    return random.choice(themes)

def generate_image(theme: dict, objects_key: str, output_path: Path) -> bool:
    """Generate image using nano-banana for a specific objects variant."""
    objects = theme.get(objects_key, theme.get("objects", "cute shapes"))
    prompt = STYLE_PROMPT.format(
        objects=objects,
        text=theme.get("text", "")
    )

    try:
        result = subprocess.run(
            [
                "python3", str(NANO_BANANA),
                prompt,
                "--aspect-ratio", "3:4",
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
    tags = random.sample(CORE_TAGS, 3) + random.sample(PILLAR_TAGS.get(pillar, ["#涂鸦"]), 1)
    tags.append("#BingBang")
    tag_line = " ".join(tags)
    return f"{base_caption}\n\n{tag_line}"

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    day_of_week = datetime.now().weekday()

    themes_data = parse_theme_bank()
    pillar = PILLARS[day_of_week]
    theme = pick_theme(themes_data, pillar)

    output_dir = DRAFTS_DIR / today
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📅 Date: {today}")
    print(f"🎯 Pillar: {pillar}")
    print(f"💡 Text: {theme.get('text')}")
    print(f"🎨 Option A: {theme.get('objects')}")
    print(f"🎨 Option B: {theme.get('objects_alt', '(no alt — using same)')}")
    print()

    # Generate Option A
    image_a = output_dir / "image_a.png"
    print("🎨 Generating Option A...")
    success_a = generate_image(theme, "objects", image_a)
    print(f"   {'✅' if success_a else '❌'} Option A {'saved' if success_a else 'failed'}")

    # Generate Option B
    image_b = output_dir / "image_b.png"
    print("🎨 Generating Option B...")
    if theme.get("objects_alt"):
        success_b = generate_image(theme, "objects_alt", image_b)
    else:
        # Fallback: use same objects (shouldn't happen once theme bank is updated)
        success_b = generate_image(theme, "objects", image_b)
    print(f"   {'✅' if success_b else '❌'} Option B {'saved' if success_b else 'failed'}")

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
        "images": {
            "a": str(image_a),
            "b": str(image_b),
        },
        # Keep backward compat
        "image": str(image_a),
        "generated_at": datetime.now().isoformat(),
    }
    meta_path = output_dir / "metadata.json"
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📋 Metadata saved to {meta_path}")

    print()
    print("=" * 40)
    print(f"📄 Caption:\n{caption}")
    print("=" * 40)

    return 0 if (success_a and success_b) else 1

if __name__ == "__main__":
    sys.exit(main())
