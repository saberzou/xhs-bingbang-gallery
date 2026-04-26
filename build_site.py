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
    <title>@BingBang Gallery</title>
    <style>
        :root {{
            --bg: #FFFFFF;
            --text: #333;
            --text-sub: #999;
            --accent: #FF2442;
            --gap: 6px;
            --radius: 6px;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            -webkit-font-smoothing: antialiased;
        }}
        header {{
            padding: 28px 16px 20px;
            text-align: center;
        }}
        header h1 {{
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        header p {{
            color: var(--text-sub);
            font-size: 12px;
            margin-top: 4px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: var(--gap);
            padding: 0 var(--gap) var(--gap);
            max-width: 1200px;
            margin: 0 auto;
        }}
        @media (min-width: 640px) {{ .grid {{ grid-template-columns: repeat(3, 1fr); }} }}
        @media (min-width: 960px) {{ .grid {{ grid-template-columns: repeat(4, 1fr); }} }}
        @media (min-width: 1280px) {{ .grid {{ grid-template-columns: repeat(5, 1fr); }} }}
        .item {{
            cursor: pointer;
        }}
        .item-img {{
            position: relative;
            width: 100%;
            border-radius: var(--radius);
            overflow: hidden;
            background: #f5f5f5;
            border: 1px solid rgba(0,0,0,0.06);
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
            background: rgba(0,0,0,0.5);
            color: #fff;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .item-info {{
            padding: 6px 2px 14px;
        }}
        .item-title {{
            font-size: 12px;
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
            margin-top: 4px;
            font-size: 10px;
            color: var(--text-sub);
        }}
        .item-author {{
            display: flex;
            align-items: center;
            gap: 3px;
        }}

        /* Lightbox */
        .lightbox {{
            display: none;
            position: fixed;
            inset: 0;
            z-index: 100;
            background: rgba(0,0,0,0.92);
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }}
        .lightbox.open {{ display: flex; }}
        .lightbox img {{
            max-width: 90vw;
            max-height: 70vh;
            border-radius: 8px;
        }}
        .lightbox-caption {{
            color: #fff;
            font-size: 14px;
            margin-top: 16px;
            max-width: 480px;
            text-align: center;
            line-height: 1.6;
            padding: 0 20px;
            white-space: pre-wrap;
        }}
        .lightbox-actions {{
            margin-top: 16px;
            display: flex;
            gap: 12px;
        }}
        .lightbox-actions button, .lightbox-actions a {{
            background: rgba(255,255,255,0.15);
            border: none;
            color: #fff;
            padding: 8px 20px;
            border-radius: 100px;
            font-size: 13px;
            cursor: pointer;
            text-decoration: none;
        }}
        .lightbox-actions button:hover, .lightbox-actions a:hover {{ background: rgba(255,255,255,0.25); }}
        .lightbox-close {{
            position: absolute;
            top: 16px;
            right: 20px;
            background: none;
            border: none;
            color: #fff;
            font-size: 28px;
            cursor: pointer;
        }}
        .lightbox-nav {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255,255,255,0.15);
            border: none;
            color: #fff;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 18px;
            cursor: pointer;
        }}
        .lightbox-nav:hover {{ background: rgba(255,255,255,0.25); }}
        .lightbox-nav.prev {{ left: 16px; }}
        .lightbox-nav.next {{ right: 16px; }}
        .lightbox-dots {{
            display: flex;
            gap: 6px;
            margin-top: 12px;
        }}
        .lightbox-dots span {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: rgba(255,255,255,0.3);
            cursor: pointer;
        }}
        .lightbox-dots span.active {{ background: #fff; }}
    </style>
</head>
<body>

    <header>
        <h1>@BingBang</h1>
        <p>Sage & Andy's daily adventures</p>
    </header>

    <div class="grid">
        {cards}
    </div>

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
            <a id="lb-download" href="" download="">Save Image</a>
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

            // Nav buttons
            document.getElementById('lb-prev').style.display = lbImages.length > 1 ? 'block' : 'none';
            document.getElementById('lb-next').style.display = lbImages.length > 1 ? 'block' : 'none';

            // Dots
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
