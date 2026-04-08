# XHS Creator — Project Context

_Read this file at the start of any session involving this project._
_Last updated: 2026-04-08_

---

## What Is This

A daily content generation pipeline for Saber's 小红书 account **@BingBang** (42k+ likes/collections). Generates minimalist B&W doodles + Chinese captions + hashtags, saved locally for Saber to grab and post.

Profile: https://www.xiaohongshu.com/user/profile/63cdd10e00000000260059b0

## Current Status: TESTING

Output quality is being evaluated before adopting as daily workflow. Not yet in production/cron.

## What's Built

- `generate.py` — main script, picks pillar by day of week, random theme, generates image via Gemini Imagen (nano-banana), writes caption + metadata
- `style-guide.md` — visual identity, caption voice, hashtag strategy
- `themes/theme-bank.md` — 50 themes across 5 pillars
- `drafts/samples/` — 5 test outputs (one per pillar)

## File Layout

```
projects/xhs-creator/
├── PROJECT-CONTEXT.md    ← YOU ARE HERE
├── README.md             ← user-facing docs
├── generate.py           ← main generation script
├── style-guide.md        ← visual + caption rules
├── themes/theme-bank.md  ← all 50 themes
└── drafts/
    ├── samples/          ← test batch (5 images)
    │   ├── 01-design-negative-space.png  ← too empty/literal
    │   ├── 02-life-headphones.png        ← ✅ strong
    │   ├── 03-emotion-deadline.png       ← ✅ strong ("this is fine" energy)
    │   ├── 04-typography-suanle.png      ← ⚠️ Chinese text garbled
    │   └── 05-creative-bubbles.png       ← ✅ strong
    └── YYYY-MM-DD/       ← daily output (when running)
```

## Visual Style Target

- B&W line drawings, iPad doodle aesthetic
- Minimalist, hand-drawn feel. Not polished illustration.
- Simple lines on pure white background
- No color, no shading, no gray
- Abstract concepts made visual, everyday objects with twist
- Like a designer's notebook margins

## Image Generation

- Tool: `nano-banana` (Gemini Imagen via `gemini-2.5-flash-image`)
- Aspect ratio: 3:4 (XHS preferred)
- Script: `~/.openclaw/workspace-axel/skills/nano-banana/generate_image.py`
- All prompts include "No text, no words, no labels, no letters" (except typography pillar)

## Content Pillars (daily rotation)

| Day | Pillar | Vibe |
|-----|--------|------|
| Mon | 设计感悟 | Design observations |
| Tue | 生活碎片 | Life fragments |
| Wed | 创意灵感 | Creative sparks |
| Thu | 文字涂鸦 | Word art |
| Fri | 情绪速写 | Emotion sketches |
| Sat | 设计感悟 | Design |
| Sun | 生活碎片 | Life |

## Known Issues

1. **Typography pillar (文字涂鸦)**: Gemini garbles Chinese characters. Need to generate plain doodle background + overlay real Chinese text via PIL/Pillow or ImageMagick
2. **Negative space themes**: Can come out too empty/boring (looks like an error). Need more visual anchor points
3. **No XHS login yet**: Can't pull Saber's actual post data to calibrate style. Needs QR code login via `xhs login --qrcode` when Saber is available
4. **Consistency**: Some outputs are more "illustration" than "doodle". Prompt refinement needed per pillar

## Next Steps (Priority Order)

1. Fix typography pillar (code-based text overlay)
2. Refine prompts for more consistent doodle style (less illustrative, more sketchy)
3. Handle edge cases (negative space themes need more elements)
4. XHS login → pull real posts → calibrate style guide
5. Set up as daily cron once quality is approved

## How to Run

```bash
# Generate today's content
python3 ~/. openclaw/workspace-axel/projects/xhs-creator/generate.py

# Output goes to drafts/YYYY-MM-DD/
#   image.png, caption.md, metadata.json
```

## Design Decisions

- Captions are short (1-3 sentences). The drawing speaks, words whisper.
- Hashtags: 3 core + 1 pillar-specific + #BingBang
- Titles are the quote itself (truncated to first clause if >20 chars)
- Themes chosen randomly within each day's pillar for variety

---

_This file is the single source of truth for project state. Update it when things change._
