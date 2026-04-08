# XHS Creator — Daily Content Pipeline for @BingBang

## What This Is

Generates daily 小红书 content matching your minimalist B&W doodle style.
Each day: one image + one caption + hashtags, saved locally for you to grab and post.

## Quick Use

```bash
# Generate today's content
python3 ~/. openclaw/workspace-axel/projects/xhs-creator/generate.py

# Content lands in:
# projects/xhs-creator/drafts/YYYY-MM-DD/
#   ├── image.png     ← the doodle
#   ├── caption.md    ← title + caption + hashtags
#   └── metadata.json ← theme info
```

## How It Works

1. **Picks today's pillar** based on day of week (design → life → creative → typography → emotion, repeats)
2. **Selects a random theme** from the theme bank (50+ themes across 5 pillars)
3. **Generates a B&W doodle** via Gemini Imagen (nano-banana), 3:4 aspect ratio
4. **Writes caption** with quote + curated hashtags
5. **Saves everything** to `drafts/YYYY-MM-DD/`

## Content Pillars

| Day | Pillar | Vibe |
|-----|--------|------|
| Mon | 设计感悟 | Design observations |
| Tue | 生活碎片 | Life fragments |
| Wed | 创意灵感 | Creative sparks |
| Thu | 文字涂鸦 | Word art |
| Fri | 情绪速写 | Emotion sketches |
| Sat | 设计感悟 | Design |
| Sun | 生活碎片 | Life |

## Files

```
projects/xhs-creator/
├── README.md              ← you're here
├── generate.py            ← main generation script
├── style-guide.md         ← visual + caption rules
├── themes/theme-bank.md   ← all 50+ themes
├── drafts/                ← daily output
│   └── YYYY-MM-DD/
│       ├── image.png
│       ├── caption.md
│       └── metadata.json
└── reference-posts/       ← (future) analyzed XHS posts
```

## After XHS Login

Once `xhs login --qrcode` is done:
1. Pull your top posts → analyze patterns
2. Refine style guide with real data
3. Optionally auto-post via `xhs` CLI (with your approval)

## Cron (optional)

```bash
# Add to crontab for daily 8am generation
0 8 * * * python3 /Users/saberzou/.openclaw/workspace-axel/projects/xhs-creator/generate.py
```
