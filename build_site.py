import json
import os
import shutil
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
DRAFTS_DIR = SCRIPT_DIR / "drafts"
DOCS_DIR = SCRIPT_DIR / "docs"
IMG_OUTPUT_DIR = DOCS_DIR / "images"

# Ensure output directories exist
DOCS_DIR.mkdir(parents=True, exist_ok=True)
IMG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@BingBang — Sage & Andy</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #faf9f7;
            --surface: #ffffff;
            --text: #000000;
            --text-sub: #696f7b;
            --border: #cfcfcf;
            --accent: #ade900;
            --accent-fill: #ebffb1;
            --orange: #d8723c;
            --radius: 10px;
            --radius-pill: 999px;
            --gap: 16px;
            --shadow: rgba(34, 40, 42, 0.04) 0px 3px 10px 0px;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            -webkit-font-smoothing: antialiased;
            min-height: 100vh;
        }}
        .hero {{
            padding: 68px 24px 40px;
            text-align: center;
            background: linear-gradient(rgb(242, 241, 237) 42%, rgb(213, 223, 224) 94%, rgb(229, 255, 148) 104%);
        }}
        .hero h1 {{
            font-size: 42px;
            font-weight: 700;
            letter-spacing: -1px;
            line-height: 1.1;
        }}
        .hero p {{
            color: var(--text-sub);
            font-size: 16px;
            margin-top: 12px;
            font-weight: 400;
            letter-spacing: 0.1px;
        }}
        .hero .tag {{
            display: inline-block;
            margin-top: 20px;
            background: var(--accent-fill);
            border: 1px solid var(--accent);
            color: var(--text);
            font-size: 13px;
            font-weight: 500;
            padding: 6px 16px;
            border-radius: var(--radius-pill);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: var(--gap);
            padding: 32px 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        @media (min-width: 640px) {{ .grid {{ grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 40px 24px; }} }}
        @media (min-width: 960px) {{ .grid {{ grid-template-columns: repeat(4, 1fr); }} }}
        @media (min-width: 1280px) {{ .grid {{ grid-template-columns: repeat(5, 1fr); }} }}
        .item {{
            cursor: pointer;
            transition: transform 0.2s ease;
        }}
        .item:hover {{
            transform: translateY(-4px);
        }}
        .item-img {{
            position: relative;
            width: 100%;
            border-radius: var(--radius);
            overflow: hidden;
            background: var(--surface);
            box-shadow: var(--shadow);
        }}
        .item-img img {{
            display: block;
            width: 100%;
            aspect-ratio: 1;
            object-fit: cover;
        }}
        .item-img .multi-badge {{
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(0,0,0,0.6);
            color: #fff;
            font-size: 10px;
            font-weight: 500;
            padding: 3px 8px;
            border-radius: var(--radius-pill);
        }}
        .item-info {{
            padding: 8px 2px 16px;
        }}
        .item-title {{
            font-size: 13px;
            font-weight: 500;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        .item-meta {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 6px;
            font-size: 11px;
            color: var(--text-sub);
        }}
        .item-author {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-weight: 500;
        }}

        /* Lightbox */
        .lightbox {{
            display: none;
            position: fixed;
            inset: 0;
            z-index: 100;
            background: rgba(0,0,0,0.88);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }}
        .lightbox.open {{ display: flex; }}
        .lightbox img {{
            max-width: 90vw;
            max-height: 68vh;
            border-radius: var(--radius);
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
        }}
        .lightbox-caption {{
            color: #fff;
            font-size: 14px;
            margin-top: 20px;
            max-width: 480px;
            text-align: center;
            line-height: 1.6;
            padding: 0 20px;
            white-space: pre-wrap;
            opacity: 0.9;
        }}
        .lightbox-actions {{
            margin-top: 20px;
            display: flex;
            gap: 12px;
        }}
        .lightbox-actions button, .lightbox-actions a {{
            background: transparent;
            border: 1px solid rgba(255,255,255,0.3);
            color: #fff;
            padding: 8px 20px;
            border-radius: var(--radius-pill);
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s;
        }}
        .lightbox-actions button:hover, .lightbox-actions a:hover {{
            background: rgba(255,255,255,0.12);
            border-color: rgba(255,255,255,0.5);
        }}
        .lightbox-close {{
            position: absolute;
            top: 20px;
            right: 24px;
            background: none;
            border: none;
            color: #fff;
            font-size: 28px;
            cursor: pointer;
            opacity: 0.7;
            transition: opacity 0.2s;
        }}
        .lightbox-close:hover {{ opacity: 1; }}
        .lightbox-nav {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: transparent;
            border: 1px solid rgba(255,255,255,0.2);
            color: #fff;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 18px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .lightbox-nav:hover {{ background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.4); }}
        .lightbox-nav.prev {{ left: 20px; }}
        .lightbox-nav.next {{ right: 20px; }}
        .lightbox-dots {{
            display: flex;
            gap: 6px;
            margin-top: 14px;
        }}
        .lightbox-dots span {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: rgba(255,255,255,0.3);
            cursor: pointer;
            transition: all 0.2s;
        }}
        .lightbox-dots span.active {{ background: var(--accent); transform: scale(1.3); }}

        footer {{
            text-align: center;
            padding: 40px 20px;
            font-size: 12px;
            color: var(--text-sub);
        }}
        footer a {{
            color: var(--text);
            text-decoration: none;
            border-bottom: 1px solid var(--border);
        }}
    </style>
</head>
<body>

    <div class="hero">
        <h1>Sage & Andy</h1>
        <p>A quiet doodle world. Gentle reminders for everyday life.</p>
        <span class="tag">@BingBang</span>
    </div>

    <div class="grid">
        {cards}
    </div>

    <footer>
        Small moments, shared softly. &mdash; <a href="https://www.xiaohongshu.com/user/profile/5a20b5c04eacab4a9e38ea26" target="_blank">@BingBang on XHS</a>
    </footer>

    <!-- Lightbox -->
    <div class="lightbox" id="lightbox">
        <button class="lightbox-close" onclick="closeLightbox()">&times;</button>
        <button class="lightbox-nav prev" id="lb-prev" onclick="lbNav(-1)">&#8249;</button>
        <button class="lightbox-nav next" id="lb-next" onclick="lbNav(1)">&#8250;</button>
        <img id="lb-img" src="" alt="">
        <div class="lightbox-dots" id="lb-dots"></div>
        <div class="lightbox-caption" id="lb-caption"></div>
        <div class="lightbox-actions">
            <button onclick="lbCopy()">Copy Caption</button>
            <a id="lb-download" href="" download="">Save</a>
        </div>
    </div>

    <script>
        let lbImages = [];
        let lbIndex = 0;
        let lbCaption = '';

        function openLightbox(images, caption, startIdx) {{
            lbImages = images;
            lbIndex = startIdx || 0;
            lbCaption = caption;
            updateLb();
            document.getElementById('lightbox').classList.add('open');
            document.body.style.overflow = 'hidden';
        }}

        function closeLightbox() {{
            document.getElementById('lightbox').classList.remove('open');
            document.body.style.overflow = '';
        }}

        function lbNav(dir) {{
            lbIndex = (lbIndex + dir + lbImages.length) % lbImages.length;
            updateLb();
        }}

        function updateLb() {{
            const img = document.getElementById('lb-img');
            img.src = lbImages[lbIndex];
            document.getElementById('lb-caption').textContent = lbCaption;
            const dl = document.getElementById('lb-download');
            dl.href = lbImages[lbIndex];
            dl.download = lbImages[lbIndex].split('/').pop();

            document.getElementById('lb-prev').style.display = lbImages.length > 1 ? 'block' : 'none';
            document.getElementById('lb-next').style.display = lbImages.length > 1 ? 'block' : 'none';

            const dots = document.getElementById('lb-dots');
            if (lbImages.length > 1) {{
                dots.innerHTML = lbImages.map((_, i) =>
                    `<span class="${{i === lbIndex ? 'active' : ''}}" onclick="lbIndex=${{i}};updateLb()"></span>`
                ).join('');
                dots.style.display = 'flex';
            }} else {{
                dots.style.display = 'none';
            }}
        }}

        function lbCopy() {{
            navigator.clipboard.writeText(lbCaption).then(() => {{
                const btn = event.target;
                btn.textContent = 'Copied!';
                setTimeout(() => btn.textContent = 'Copy Caption', 1500);
            }});
        }}

        document.getElementById('lightbox').addEventListener('click', (e) => {{
            if (e.target === e.currentTarget) closeLightbox();
        }});

        document.addEventListener('keydown', (e) => {{
            if (!document.getElementById('lightbox').classList.contains('open')) return;
            if (e.key === 'Escape') closeLightbox();
            if (e.key === 'ArrowLeft') lbNav(-1);
            if (e.key === 'ArrowRight') lbNav(1);
        }});
    </script>
</body>
</html>
"""

CARD_TEMPLATE = """
        <div class="item" onclick="openLightbox({images_json}, `{escaped_caption}`, 0)">
            <div class="item-img">
                <img src="images/{first_image_filename}" alt="{title}" loading="lazy">
                {multi_badge}
            </div>
            <div class="item-info">
                <div class="item-title">{title}</div>
                <div class="item-meta">
                    <span class="item-author">🐯 BingBang</span>
                    <span>{date}</span>
                </div>
            </div>
        </div>
"""


def build():
    cards_html = []

    if not DRAFTS_DIR.exists():
        print("No drafts directory found.")
        return

    date_folders = sorted([d for d in DRAFTS_DIR.iterdir() if d.is_dir() and d.name != "samples"], reverse=True)

    for folder in date_folders:
        meta_file = folder / "metadata.json"
        caption_file = folder / "caption.md"

        images_to_show = []

        if meta_file.exists() and caption_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            with open(caption_file, 'r', encoding='utf-8') as f:
                caption = f.read().strip()

            # Check for multiple images in metadata (v2 format)
            if "images" in meta:
                images_to_show = [Path(p) for p in meta["images"].values()]
            elif "image" in meta:
                images_to_show = [Path(meta["image"])]

            # Also pick up image_a.png / image_b.png even if metadata is v1
            if len(images_to_show) <= 1:
                img_a = folder / "image_a.png"
                img_b = folder / "image_b.png"
                if img_a.exists() and img_b.exists():
                    images_to_show = [img_a, img_b]
        else:
            # Fallback
            caption = caption_file.read_text(encoding='utf-8').strip() if caption_file.exists() else "Test generation."
            meta = {"date": folder.name, "pillar": "测试"}
            images_to_show = list(folder.glob("*.png"))

        # Filter to only existing images
        images_to_show = [img for img in images_to_show if img.exists()]

        if not images_to_show:
            continue

        image_filenames = []
        first_img_filename = ""

        for idx, img_path in enumerate(images_to_show):
            img_filename = f"{folder.name}_{img_path.name}"
            if idx == 0:
                first_img_filename = img_filename

            target_img = IMG_OUTPUT_DIR / img_filename
            shutil.copy2(img_path, target_img)
            image_filenames.append(f"images/{img_filename}")

        # Title: first line of caption, truncated
        title = caption.split('\n')[0][:60]

        escaped_caption = caption.replace('`', '\\`').replace('$', '\\$')
        images_json = json.dumps(image_filenames)

        multi_badge = ""
        if len(images_to_show) > 1:
            multi_badge = f'<span class="multi-badge">{len(images_to_show)} pics</span>'

        card = CARD_TEMPLATE.format(
            images_json=images_json,
            escaped_caption=escaped_caption,
            first_image_filename=first_img_filename,
            title=title,
            multi_badge=multi_badge,
            date=meta['date'],
        )
        cards_html.append(card)

    final_html = HTML_TEMPLATE.format(cards="\n".join(cards_html))

    index_file = DOCS_DIR / "index.html"
    index_file.write_text(final_html, encoding='utf-8')
    print(f"✅ Website built successfully at {index_file}")

if __name__ == "__main__":
    build()
