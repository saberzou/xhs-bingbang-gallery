#!/usr/bin/env python3
"""
XHS Daily Content Generator for @BingBang — Sage & Andy Edition
Generates one doodle per day featuring Sage (bear) and/or Andy (cat).
Output: drafts/YYYY-MM-DD/ with image.png, caption.md, metadata.json

Scenes are generated FRESH each day by an LLM, grounded in the WORLD-BIBLE
and instructed to avoid recent posts. No more cycling through a fixed list.
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
REFS_DIR = SCRIPT_DIR / "references"
NANO_BANANA = Path.home() / ".openclaw/workspace-axel/skills/nano-banana/generate_image.py"

# Model for scene ideation. Sonnet handles creative + grounded constraints well.
IDEATION_MODEL = os.environ.get("XHS_IDEATION_MODEL", "github-copilot/claude-opus-4.7")
LOOKBACK_DAYS = 30  # how many recent posts to feed as exclusion context

# --- Character Definitions ---

SAGE_DESC = """a bear character called Sage with a large rounded-rectangle head (wider than tall, flat top and bottom with soft radiused corners), two small round semi-circular ear nubs on the outer top corners of the head, two tiny solid black dot eyes set very far apart near outer edges of face, a minimalist "I"-shaped face feature centered between the eyes (tiny horizontal dash for nose, short vertical line down, tiny horizontal dash for mouth). Squat chibi body roughly same height as head, short tubular limbs with rounded nub hands. Wearing a white t-shirt with a small outlined heart (♡) on the chest and solid black shorts. Simple rounded shoes. Clean consistent line weight throughout."""

ANDY_DESC = """a cat character called Andy with an identical rounded-rectangle head shape to Sage, but with three thick vertical parallel black stripes (|||) centered on the top of the forehead as the key distinguishing feature, small slightly pointed triangular ears on the top corners of the head, identical tiny solid black dot eyes set very far apart, identical minimalist "I"-shaped face feature. Same squat chibi body proportions as Sage. Wearing a white t-shirt (plain, no icon) and solid black shorts. Simple rounded shoes. Clean consistent line weight throughout."""

STYLE_BASE = """Clean digital monolinear ink illustration on pure white background. Constant line thickness throughout (no tapering or pressure sensitivity). Flat 2D perspective, no shading. Extremely high use of negative space. A single simple horizontal line represents the ground. Characters centered in frame. Simplified props (maximum 1-2 objects). Optional: a few four-pointed diamond sparkles (✦) or short parallel motion lines. Hand-drawn minimalist sans-serif text at the very bottom in all-caps with rounded terminals reading exactly: "{text}" """

# --- Legacy Content Scenes (kept as seed/fallback examples only) ---
# These are NO LONGER selected from directly. The LLM uses them as tone/format examples.
_LEGACY_SEED_SCENES = [
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

    # --- WORLD-BIBLE HOOKS (anchored to references/WORLD-BIBLE.md) ---
    # These are continuity-rich scenes pulled from the iceberg under the doodle.
    # Each has an explicit bible_hook field so metadata captures the source.
    {"cast": "both", "text": "JUST ONE PEEK", "caption": "说好只看一眼。", "scene": "late evening kitchen, Sage caught reaching into an open low drawer with simple snack bag rectangles inside, Andy on a sofa in background scrolling a phone with one earbud in (the other ear empty), a small round wall clock above showing 10:30", "bible_hook": "§3 snack drawer + §6 missing AirPod"},
    {"cast": "andy", "text": "AIRPOD MIA", "caption": "剩一只也能听。", "scene": "Andy in oversized t-shirt patting the sofa cushions looking for something, one ear has a tiny earbud, a couple of question marks floating, a remote and a takeout box on the table", "bible_hook": "§6 Andy lost an AirPod Tuesday"},
    {"cast": "sage", "text": "LEG DAY", "caption": "下雨也是腿日。", "scene": "Sage stepping out the apartment door with a small gym bag over shoulder, a tiny umbrella in the other hand, a few rain lines outside, a single barbell icon faintly above as a thought", "bible_hook": "§2 Sage gym 4x/week + §6 rain on leg day"},
    {"cast": "sage", "text": "LIGHT IS RIGHT", "caption": "这个光不接不行。", "scene": "Sage crouching on a sidewalk holding up a small camera (rounded rectangle with a circle lens) toward something off-frame, a leaf casting a tiny shadow line, two diamond sparkles", "bible_hook": "§2 Sage street photography (Fuji X100VI)"},
    {"cast": "andy", "text": "NEW DROP", "caption": "又安了一个花呗。", "scene": "Andy on the sofa staring at a phone screen showing a tiny shopping bag icon, one paw on chin in deliberation, a small shopping bag already on the floor next to him", "bible_hook": "§3 Andy luxury retail + 14 active 花呗 plans"},
    {"cast": "both", "text": "DAY 3 LASAGNA", "caption": "剩菜也是一种愿意。", "scene": "both at a small kitchen table each with a square plate, one large rectangular dish in the middle, the dish noticeably emptier than full, a single fork in the air mid-bite", "bible_hook": "§6 Wednesday's lasagna day 3"},
    {"cast": "sage", "text": "BASIL LIVES", "caption": "罗勒又活过来了。", "scene": "Sage on a narrow balcony crouched watering a small potted basil plant with a tiny watering can, a folding stool beside, a thin railing line", "bible_hook": "§6 the basil is making a comeback"},
    {"cast": "andy", "text": "23:30 RUN", "caption": "夜粉应急补给。", "scene": "Andy in oversized t-shirt and slippers walking back through a doorway carrying a small convenience-store bag with simple snack rectangles poking out, a wall clock showing 23:30", "bible_hook": "§6 emergency 7-Eleven snack run"},
    {"cast": "both", "text": "AC WAR", "caption": "二十四还是二十六。", "scene": "Sage and Andy each reaching for the same wall-mounted AC remote on a low table, a tiny wall-mounted AC unit visible in the corner, a small spark between their hands", "bible_hook": "§4 the 24 vs 26 AC debate"},
    {"cast": "both", "text": "DID YOU BRING IT", "caption": "你伞带了吗。", "scene": "both at the front door area, Sage holding a folded umbrella out toward Andy who is mid-step leaving, a small shoe pile on the floor, a coat hook on the wall", "bible_hook": "§4 they don't say I love you, they say did you bring an umbrella"},
    {"cast": "sage", "text": "CARDS LOGGED", "caption": "每一组都记上。", "scene": "Sage sitting on a yoga mat with a tiny phone in hand and a small dumbbell beside, a few sweat drop marks, a notebook icon faint above", "bible_hook": "§2 Sage logs every set in an app"},
    {"cast": "andy", "text": "OUTFIT READY", "caption": "明天穿什么已决定。", "scene": "Andy at night standing before a chair with a folded outfit stack laid out (t-shirt rectangle, pants rectangle, two shoe shapes underneath), one paw on chin, a tiny crescent moon outside a small window", "bible_hook": "§2 Andy plans tomorrow's outfit the night before"},
]

CORE_TAGS = ["#手绘", "#涂鸦", "#黑白", "#极简", "#插画"]
EXTRA_TAGS = ["#BingBang", "#Sage和Andy", "#日常", "#治愈", "#生活感悟"]


def load_world_bible() -> str:
    p = REFS_DIR / "WORLD-BIBLE.md"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


def get_recent_posts(days: int = LOOKBACK_DAYS) -> list[dict]:
    """Return recent posts with text, scene, bible_hook so the LLM can avoid them."""
    if not DRAFTS_DIR.exists():
        return []
    folders = sorted(
        [d for d in DRAFTS_DIR.iterdir() if d.is_dir() and d.name != "samples"],
        reverse=True,
    )[:days]
    recent = []
    for folder in folders:
        meta_path = folder / "metadata.json"
        if not meta_path.exists():
            continue
        try:
            m = json.loads(meta_path.read_text(encoding="utf-8"))
            recent.append({
                "date": m.get("date", folder.name),
                "text": m.get("text", ""),
                "caption": m.get("caption", ""),
                "scene": m.get("scene", ""),
                "cast": m.get("cast", ""),
                "bible_hook": m.get("bible_hook"),
            })
        except Exception:
            pass
    return recent


def invoke_llm(prompt: str, timeout: int = 120) -> str:
    """Run a one-shot model turn via openclaw infer."""
    result = subprocess.run(
        [
            "openclaw", "infer", "model", "run",
            "--model", IDEATION_MODEL,
            "--prompt", prompt,
            "--json",
        ],
        capture_output=True, text=True, timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(f"LLM call failed: {result.stderr[:500]}")
    # Parse the wrapper JSON, extract text content.
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout.strip()
    # openclaw infer model run shape: { outputs: [ { text } ] }
    if isinstance(data.get("outputs"), list) and data["outputs"]:
        first = data["outputs"][0]
        if isinstance(first, dict) and isinstance(first.get("text"), str):
            return first["text"]
    # Try common shapes
    for key in ("text", "content", "output", "response"):
        if isinstance(data.get(key), str):
            return data[key]
    # message/choices style
    if isinstance(data.get("message"), dict) and isinstance(data["message"].get("content"), str):
        return data["message"]["content"]
    if isinstance(data.get("choices"), list) and data["choices"]:
        ch = data["choices"][0]
        if isinstance(ch, dict):
            if isinstance(ch.get("text"), str):
                return ch["text"]
            if isinstance(ch.get("message"), dict) and isinstance(ch["message"].get("content"), str):
                return ch["message"]["content"]
    # Fall back to raw stdout
    return result.stdout


def extract_json_object(text: str) -> dict:
    """Extract the first JSON object from arbitrary LLM text."""
    # Strip code fences
    t = text.strip()
    if t.startswith("```"):
        # Remove leading fence line and trailing fence
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    # Find first { and matching }
    start = t.find("{")
    if start < 0:
        raise ValueError(f"No JSON object found in LLM output: {text[:300]}")
    depth = 0
    for i in range(start, len(t)):
        if t[i] == "{":
            depth += 1
        elif t[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(t[start:i+1])
    raise ValueError(f"Unterminated JSON object in LLM output: {text[:300]}")


def generate_scene(world_bible: str, recent: list[dict], seed_examples: list[dict]) -> dict:
    """Ask the LLM to invent today's scene grounded in the world bible."""
    recent_lines = []
    for r in recent:
        hook = f" [{r['bible_hook']}]" if r.get("bible_hook") else ""
        recent_lines.append(f"- {r['date']}: {r['cast']:>4} | \"{r['text']}\" — {r['scene']}{hook}")
    recent_block = "\n".join(recent_lines) if recent_lines else "(none yet)"

    examples = random.sample(seed_examples, k=min(6, len(seed_examples)))
    ex_lines = []
    for s in examples:
        ex_lines.append(json.dumps({
            "cast": s["cast"],
            "text": s["text"],
            "caption": s["caption"],
            "scene": s["scene"],
        }, ensure_ascii=False))
    examples_block = "\n".join(ex_lines)

    prompt = f"""You are the daily scene writer for @BingBang's Sage & Andy doodle series on Xiaohongshu.
You will invent ONE fresh scene for today's post. Output a single JSON object, nothing else.

# Brand
Sage = bear roommate (gentle, designer, gym, street photography).
Andy = cat roommate (luxury retail, snacks, lost AirPods, scrolling).
Minimalist black-and-white doodles. One short English caption inside the drawing, one short Chinese caption beneath.

# Format you must output (single JSON object, no prose, no code fence)
{{
  "cast": "both" | "sage" | "andy",
  "text": "SHORT ENGLISH CAPTION IN ALL CAPS, max ~22 chars, no punctuation except apostrophes",
  "caption": "短中文一句，结尾用句号或感叹号，不超过15字",
  "scene": "one concrete English sentence describing the drawing: posture, props, setting. Keep it simple — minimalist line drawing on white background.",
  "bible_hook": "§<section number> short reference to the world bible fact you anchored to",
  "rationale": "one sentence: why this scene this week, and how it differs from recent posts"
}}

# HARD RULES
1. The scene MUST anchor to a specific fact in the World Bible below. Cite it in bible_hook.
2. You MUST NOT reuse the same MOTIF as any post in the RECENT POSTS list. Motifs include: umbrella/rain, basil/plant, AirPod, snack run, coffee, outfit, gym/leg day, lasagna, AC remote, balcony, etc. If the recent list mentions "umbrella", do NOT make another umbrella scene. If it mentions "basil", no basil. Etc.
3. Avoid texts/captions that are near-paraphrases of recent ones.
4. Keep it specific and small. One concrete moment. No abstract metaphors unless grounded in a prop.
5. Vary cast: if the last 3 posts were all "both", consider a solo. If all solo, consider "both".
6. The scene must be drawable as a single minimalist line illustration. Max 1-2 props.

# WORLD BIBLE (truth source)
{world_bible}

# RECENT POSTS (last {len(recent)} days — DO NOT REPEAT THESE MOTIFS)
{recent_block}

# TONE/FORMAT EXAMPLES (for style reference only — do not copy)
{examples_block}

Now output the JSON object for today's scene."""

    raw = invoke_llm(prompt)
    scene = extract_json_object(raw)

    # Validate
    required = {"cast", "text", "caption", "scene"}
    missing = required - set(scene.keys())
    if missing:
        raise ValueError(f"LLM scene missing fields {missing}: {scene}")
    if scene["cast"] not in ("both", "sage", "andy"):
        raise ValueError(f"Invalid cast: {scene['cast']}")
    scene["text"] = scene["text"].strip().upper()
    return scene


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
                "--model", "gemini-3.1-flash-image-preview",
                "-o", str(output_path),
                "--json",
            ],
            capture_output=True, text=True, timeout=240,
        )
        data = json.loads(result.stdout)
        return data.get("status") == "success"
    except Exception as e:
        print(f"Image generation failed: {e}", file=sys.stderr)
        return False


def main():
    today = datetime.now().strftime("%Y-%m-%d")

    print("🧠 Generating fresh scene via LLM...")
    world_bible = load_world_bible()
    recent = get_recent_posts(days=LOOKBACK_DAYS)
    print(f"   Loaded {len(recent)} recent posts for de-duplication.")

    # Try LLM ideation; on failure, fall back to a non-recent legacy scene.
    try:
        scene = generate_scene(world_bible, recent, _LEGACY_SEED_SCENES)
        print(f"   ✅ LLM scene generated.")
        if scene.get("rationale"):
            print(f"   💭 {scene['rationale']}")
    except Exception as e:
        print(f"   ❌ LLM ideation failed: {e}", file=sys.stderr)
        print("   ⤵️  Falling back to legacy scene pool.", file=sys.stderr)
        recent_texts = {r["text"] for r in recent}
        pool = [s for s in _LEGACY_SEED_SCENES if s["text"] not in recent_texts] or _LEGACY_SEED_SCENES
        scene = random.choice(pool)

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
        "caption": scene["caption"],
        "scene": scene["scene"],
        "bible_hook": scene.get("bible_hook"),
        "rationale": scene.get("rationale"),
        "ideation_model": IDEATION_MODEL,
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
