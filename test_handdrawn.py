import subprocess
import json
import sys
from pathlib import Path

NANO_BANANA = Path.home() / ".openclaw/workspace-axel/skills/nano-banana/generate_image.py"
OUT_PATH = Path("/Users/saberzou/.openclaw/workspace-axel/projects/xhs-creator/drafts/2026-04-08/handdrawn_test.png")

prompt = """A cute, imperfect hand-drawn black and white marker sketch on a pure white background. 
Style: Looks like it was genuinely doodled in a sketchbook with a thick black Sharpie pen. Organic, slightly wobbly lines, charming imperfections, not perfectly straight or vector-like. Bold outlines and solid ink scribbled fills.
Must include exactly 4 floating 4-pointed diamond sparkle stars (✦) with hand-drawn, slightly uneven edges.
The objects should be clustered in the center, floating. No gray tones, strictly black and white ink.
Draw these specific objects: A cute, oversized medical Band-Aid (plaster) with a tiny smiling face. Out of the top of the Band-Aid, a delicate, happy little flower is growing. 
At the very bottom, centered in an imperfect, organic hand-lettered italic font, write exactly this text: "Healing takes time."
"""

result = subprocess.run([
    "python3", str(NANO_BANANA),
    prompt,
    "--aspect-ratio", "1:1",
    "-o", str(OUT_PATH),
    "--json"
], capture_output=True, text=True)

print(result.stdout)
