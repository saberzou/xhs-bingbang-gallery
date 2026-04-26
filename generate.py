#!/usr/bin/env python3
"""
XHS Daily Content Generator for @BingBang — Sage & Andy Edition
Generates one doodle per day featuring Sage (bear) and/or Andy (cat).
Output: drafts/YYYY-MM-DD/ with image.png, caption.md, metadata.json
"""

import json
import os
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DRAFTS_DIR = SCRIPT_DIR / "drafts"
NANO_BANANA = Path.home() / ".openclaw/workspace-axel/skills/nano-banana/generate_image.py"

# --- Character Definitions ---

SAGE_DESC = """a bear character called Sage with a large rounded-rectangle head (wider than tall, flat top/bottom with soft radiused corners), two small semi-circular ear nubs on the outer top corners, two tiny solid black dot eyes set far apart near the outer edges, a minimalist nose-mouth shaped like a tiny "I" (horizontal dash nose, short vertical line, horizontal dash mouth) centered between eyes. Squat chibi body roughly same height as head, short tubular limbs with rounded nub hands, wearing a plain white t-shirt with a small solid black heart on chest and loose trousers bunching at ankles over simple rounded shoes"""

ANDY_DESC = """a cat character called Andy with an identical rounded-rectangle head to Sage, three thick vertical parallel black stripes centered on the forehead, small slightly pointed triangular ears on top corners, identical tiny black dot eyes set wide apart, identical minimalist "I" shaped nose-mouth. Same squat chibi proportions as Sage, wearing a black t-shirt with a small solid black diamond icon and simple pants with rounded shoes"""

STYLE_BASE = """Clean digital monolinear ink illustration on pure white background. Constant line thickness throughout (no tapering or pressure sensitivity). Flat 2D perspective, no shading. Extremely high use of negative space. A single simple horizontal line represents the ground. Characters centered in frame. Simplified props (maximum 1-2 objects). Optional: a few four-pointed diamond sparkles (✦) or short parallel motion lines. Hand-drawn minimalist sans-serif text at the very bottom in all-caps with rounded terminals reading exactly: "{text}" """

# --- Content Scenes ---
# Each scene has: cast (both/sage/andy), text, caption, scene description
SCENES = [
    # Everyday Life
    {"cast": "both", "text": "COFFEE FIRST", "caption": "先来杯咖啡。", "scene": "standing side by side each holding a tiny coffee cup, steam rising"},
    {"cast": "both", "text": "CLEANING LIFTS THE SPIRIT", "caption": "打扫完心情也亮了。", "scene": "Sage sweeping with a tiny broom while Andy wipes a window, sparkles around them"},
    {"cast": "sage", "text": "SLOW MORNING", "caption": "慢慢来的早晨。", "scene": "sitting on the ground holding a warm mug with both hands, eyes peacefully closed (curved lines), tiny steam swirls"},
    {"cast": "andy", "text": "JUST LOOKING", "caption": "就看看而已。", "scene": "standing on tiptoes peering into a tiny fishbowl with a small fish inside"},
    {"cast": "both", "text": "GROCERIES", "caption": "买菜也是一种仪式感。", "scene": "walking together carrying a paper grocery bag between them, a carrot and baguette sticking out"},
    {"cast": "both", "text": "LAUNDRY DAY", "caption": "晾衣服的下午。", "scene": "hanging tiny shirts on a clothesline, a small basket on the ground"},
    {"cast": "sage", "text": "NAPPING", "caption": "午睡是正经事。", "scene": "curled up sleeping on a tiny cushion, three Z letters floating above"},
    {"cast": "andy", "text": "WINDOW SEAT", "caption": "窗边发呆时间。", "scene": "sitting on a windowsill looking outside, chin resting on one hand"},

    # Growth & Emotion
    {"cast": "andy", "text": "IT'S OKAY", "caption": "没关系的。", "scene": "sitting alone hugging knees with a small rain cloud above, but a tiny smile"},
    {"cast": "both", "text": "ONE STEP AT A TIME", "caption": "一步一步来。", "scene": "climbing a simple staircase together, Sage one step ahead reaching back toward Andy"},
    {"cast": "sage", "text": "TRUST YOUR GUT", "caption": "相信直觉。", "scene": "standing confidently with arms crossed, eyes as small determined dots"},
    {"cast": "andy", "text": "STILL LEARNING", "caption": "还在学。", "scene": "sitting at a tiny desk with an open book, a small question mark floating above"},
    {"cast": "both", "text": "YOUR PACE IS THE RIGHT PACE", "caption": "你的节奏就是对的。", "scene": "walking together but at slightly different strides, both looking content"},
    {"cast": "andy", "text": "BRAVE TODAY", "caption": "今天也要勇敢。", "scene": "standing in front of a closed door, one hand reaching for the doorknob, taking a breath"},
    {"cast": "sage", "text": "BREATHE", "caption": "深呼吸。", "scene": "standing with eyes closed and arms slightly out, tiny lines radiating outward like calm energy"},

    # Relationship Moments
    {"cast": "both", "text": "STILL HERE", "caption": "我还在。", "scene": "sitting back to back on the ground, leaning on each other, eyes peaceful"},
    {"cast": "both", "text": "NO WORDS NEEDED", "caption": "不用说话也可以。", "scene": "sitting side by side on a bench looking at nothing in particular, comfortable silence"},
    {"cast": "both", "text": "SHARE", "caption": "分你一半。", "scene": "Sage breaking a cookie in half and handing one piece to Andy"},
    {"cast": "both", "text": "UMBRELLA", "caption": "有伞一起撑。", "scene": "standing close under one small umbrella, tiny rain lines falling around them"},
    {"cast": "both", "text": "GOOD NIGHT", "caption": "晚安。", "scene": "lying in two tiny beds side by side, a crescent moon and star above"},
    {"cast": "both", "text": "HIGH FIVE", "caption": "击个掌！", "scene": "jumping up to high-five each other, motion lines and sparkles at the point of contact"},

    # Metaphorical Scenes
    {"cast": "both", "text": "GROW TOGETHER", "caption": "一起成长。", "scene": "each watering a small plant in a pot, the plants leaning toward each other"},
    {"cast": "sage", "text": "CARRY ON", "caption": "继续走。", "scene": "walking forward carrying a small bindle stick over shoulder, looking ahead"},
    {"cast": "andy", "text": "BLOOM", "caption": "会开花的。", "scene": "holding a tiny pot with a single flower just beginning to bloom, looking at it with wonder"},
    {"cast": "both", "text": "PAPER BOATS", "caption": "放一只纸船。", "scene": "crouching by a simple wavy line (water), placing paper boats on the surface"},
    {"cast": "both", "text": "STARGAZING", "caption": "看星星的夜晚。", "scene": "lying on the ground looking up, a few simple stars and one shooting star above"},
    {"cast": "sage", "text": "LIGHTHOUSE", "caption": "做自己的灯塔。", "scene": "standing on a tiny hill next to a simple lighthouse, looking out calmly"},
    {"cast": "andy", "text": "BUTTERFLY", "caption": "蝴蝶停了一下。", "scene": "standing still with a tiny butterfly landed on one outstretched hand, looking at it gently"},
    {"cast": "both", "text": "KITE", "caption": "放风筝的日子。", "scene": "one holding a kite string while the other watches, a simple diamond kite in the sky with a curvy tail"},
]

CORE_TAGS = ["#手绘", "#涂鸦", "#黑白", "#极简", "#插画"]
EXTRA_TAGS = ["#BingBang", "#Sage和Andy", "#日常", "#治愈", "#生活感悟"]


def build_prompt(scene: dict) -> str:
    """Build the full image generation prompt."""
    cast = scene["cast"]
    if cast == "both":
        char_desc = f"{SAGE_DESC}; and {ANDY_DESC}"
    elif cast == "sage":
        char_desc = SAGE_DESC
    else:
        char_desc = ANDY_DESC

    scene_desc = scene["scene"]
    text = scene["text"]

    prompt = f"{STYLE_BASE.format(text=text)}\n\nCharacter(s): {char_desc}\n\nScene: {scene_desc}"
    return prompt


def generate_image(prompt: str, output_path: Path) -> bool:
    """Generate image using nano-banana."""
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


def main():
    today = datetime.now().strftime("%Y-%m-%d")

    # Pick a random scene
    scene = random.choice(SCENES)

    output_dir = DRAFTS_DIR / today
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📅 Date: {today}")
    print(f"🎭 Cast: {scene['cast']}")
    print(f"💬 Text: {scene['text']}")
    print(f"🎨 Scene: {scene['scene']}")
    print()

    # Generate image
    image_path = output_dir / "image.png"
    print("🎨 Generating doodle...")
    success = generate_image(build_prompt(scene), image_path)
    print(f"   {'✅' if success else '❌'} {'Saved' if success else 'Failed'}")

    # Caption
    tags = random.sample(CORE_TAGS, 3) + random.sample(EXTRA_TAGS, 2)
    caption = f"{scene['caption']}\n\n{' '.join(tags)}"
    caption_path = output_dir / "caption.md"
    caption_path.write_text(f"{caption}\n", encoding="utf-8")
    print(f"📝 Caption saved")

    # Metadata
    metadata = {
        "date": today,
        "cast": scene["cast"],
        "text": scene["text"],
        "scene": scene["scene"],
        "image": str(image_path),
        "generated_at": datetime.now().isoformat(),
    }
    meta_path = output_dir / "metadata.json"
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📋 Metadata saved")

    print()
    print(f"📄 Caption:\n{caption}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
