#!/usr/bin/env python3
"""Generate two doodle options for today's quote."""
import subprocess, json, sys
from pathlib import Path

NANO = str(Path.home() / ".openclaw/workspace-axel/skills/nano-banana/generate_image.py")
OUT_DIR = Path(__file__).parent

STYLE_BASE = (
    "A minimalist hand-drawn doodle illustration in black ink on a pure white background. "
    "The style is indie-comic/bullet-journal kawaii-inspired with thick, uniform, slightly wobbly outlines "
    "(mimicking a felt-tip fineliner or marker). "
    "{subject} "
    "Use solid black fills for contrast on small accents. "
    "Include exactly 4-5 floating 4-pointed hollow diamond sparkles and tiny floating dots to fill negative space. "
    "Centralized floating composition with heavy use of negative space. No background grounding lines. "
    'At the very bottom, separated by a clear margin of white space, hand-lettered bold all-caps sans-serif '
    'typography with rounded terminals that reads exactly: "KEEP GOING."'
)

options = [
    {
        "label": "A",
        "subject": (
            "The subject is a cute little electric car (EV) with dot eyes and a small smile, "
            "plugged into a charging station. The charging cable loops playfully. "
            "A tiny lightning bolt icon near the plug. Solid black fills on wheels and plug."
        ),
        "output": str(OUT_DIR / "image_a.png"),
    },
    {
        "label": "B",
        "subject": (
            "The subject is a tiny wind-up toy robot with a large key in its back, "
            "walking forward with determination. It has dot eyes and a small determined mouth. "
            "One arm is raised in a little fist pump. A winding trail of tiny footprints behind it. "
            "Solid black fills on the key and feet."
        ),
        "output": str(OUT_DIR / "image_b.png"),
    },
]

for opt in options:
    prompt = STYLE_BASE.format(subject=opt["subject"])
    print(f"\n🎨 Generating Option {opt['label']}...")
    result = subprocess.run(
        ["python3", NANO, prompt, "--aspect-ratio", "3:4", "-o", opt["output"], "--json"],
        capture_output=True, text=True, timeout=120,
    )
    try:
        data = json.loads(result.stdout)
        if data.get("status") == "success":
            print(f"   ✅ Option {opt['label']} saved to {opt['output']}")
        else:
            print(f"   ❌ Option {opt['label']} failed: {data}")
    except Exception as e:
        print(f"   ❌ Option {opt['label']} error: {e}")
        print(f"   stdout: {result.stdout[:500]}")
        print(f"   stderr: {result.stderr[:500]}")

print("\n✅ Done generating both options.")
