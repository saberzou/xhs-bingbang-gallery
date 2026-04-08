import subprocess
import json
import sys
from pathlib import Path

NANO_BANANA = Path.home() / ".openclaw/workspace-axel/skills/nano-banana/generate_image.py"
OUT_PATH = Path("/Users/saberzou/.openclaw/workspace-axel/projects/xhs-creator/drafts/2026-04-08/warm_test.png")

prompt = """A cute, minimalist black and white doodle art illustration on a pure white background.
Style: Bold thick black outlines mixed with solid black shapes for contrast. Cute kawaii aesthetic where objects have tiny dot eyes and small smiles.
Must include exactly 4 or 5 floating 4-pointed diamond sparkle stars (✦) scattered around the composition.
The objects should be clustered in the center, floating, not grounded. No background elements. No gray tones, strictly black and white.
Draw these specific objects: A large, solid black umbrella gently sheltering a tiny, happy matchstick. The matchstick has a cute smiling face and a bright little flame burning on top. A few stylized raindrops hitting the top of the umbrella.
At the very bottom, centered in a bold handwritten italic font, write exactly this text: "Protect your spark."
"""

result = subprocess.run([
    "python3", str(NANO_BANANA),
    prompt,
    "--aspect-ratio", "1:1",
    "-o", str(OUT_PATH),
    "--json"
], capture_output=True, text=True)

print(result.stdout)
