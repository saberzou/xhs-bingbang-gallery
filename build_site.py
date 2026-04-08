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
            --bg-color: #F9F8F6; /* Warm paper off-white */
            --card-bg: #FFFFFF;
            --text-main: #2C2C2C; /* Soft black */
            --text-sub: #8E8E8E;
            --accent: #E85D45; /* Warm Coral/Orange */
            --accent-hover: #D14D36;
            --radius: 24px;
            --btn-radius: 100px;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            margin: 0;
            padding: 60px 24px;
            color: var(--text-main);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        header {{
            text-align: center;
            margin-bottom: 80px;
            animation: fadeInDown 0.8s ease-out;
        }}
        header h1 {{
            margin: 0;
            font-size: 36px;
            font-weight: 700;
            letter-spacing: -0.8px;
            color: var(--text-main);
        }}
        header p {{
            color: var(--text-sub);
            font-size: 16px;
            margin-top: 16px;
            font-weight: 400;
        }}
        .masonry {{
            columns: 1;
            column-gap: 24px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        @media (min-width: 640px) {{ .masonry {{ columns: 2; }} }}
        @media (min-width: 960px) {{ .masonry {{ columns: 3; }} }}
        @media (min-width: 1280px) {{ .masonry {{ columns: 4; }} }}
        
        .card {{
            background: var(--card-bg);
            border-radius: var(--radius);
            margin-bottom: 24px;
            break-inside: avoid;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
            overflow: hidden;
            transition: transform 0.4s cubic-bezier(0.165, 0.84, 0.44, 1), box-shadow 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            display: flex;
            flex-direction: column;
            animation: fadeInUp 0.8s ease-out backwards;
            border: 1px solid rgba(0,0,0,0.02);
        }}
        .card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.08);
        }}
        .card-image-wrapper {{
            position: relative;
            width: 100%;
            padding-top: 100%;
            background: #F4F4F4;
        }}
        .card img {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .card-content {{
            padding: 28px;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}
        .date {{
            font-size: 13px;
            color: var(--text-sub);
            font-weight: 500;
        }}
        .pillar-badge {{
            color: var(--accent);
            background: rgba(232, 93, 69, 0.1);
            padding: 4px 10px;
            border-radius: 100px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        .caption {{
            font-size: 15px;
            line-height: 1.6;
            margin-bottom: 28px;
            white-space: pre-wrap;
            color: var(--text-main);
        }}
        .actions {{
            display: flex;
            gap: 12px;
            margin-top: auto;
        }}
        button, .btn-download {{
            flex: 1;
            padding: 14px 16px;
            border: none;
            border-radius: var(--btn-radius);
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            text-decoration: none;
        }}
        .btn-copy {{
            background-color: #F4F4F4;
            color: var(--text-main);
        }}
        .btn-copy:hover {{
            background-color: #EBEBEB;
        }}
        .btn-download {{
            background-color: var(--accent);
            color: #FFFFFF;
        }}
        .btn-download:hover {{
            background-color: var(--accent-hover);
        }}
        .toast {{
            position: fixed;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%) translateY(20px);
            background: #2C2C2C;
            color: white;
            padding: 14px 28px;
            border-radius: var(--btn-radius);
            font-size: 14px;
            font-weight: 500;
            opacity: 0;
            pointer-events: none;
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            z-index: 1000;
            box-shadow: 0 12px 32px rgba(0,0,0,0.15);
        }}
        .toast.show {{
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }}
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes fadeInDown {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        /* Staggered load */
        .masonry .card:nth-child(1) {{ animation-delay: 0.1s; }}
        .masonry .card:nth-child(2) {{ animation-delay: 0.2s; }}
        .masonry .card:nth-child(3) {{ animation-delay: 0.3s; }}
        .masonry .card:nth-child(4) {{ animation-delay: 0.4s; }}
        .masonry .card:nth-child(5) {{ animation-delay: 0.5s; }}
    </style>
</head>
<body>

    <header>
        <h1>@BingBang Gallery</h1>
        <p>Warm & imperfect daily doodles.</p>
    </header>

    <div class="masonry">
        {cards}
    </div>

    <div id="toast" class="toast">Copied to clipboard! ✨</div>

    <script>
        function copyText(button, text) {{
            navigator.clipboard.writeText(text).then(() => {{
                const toast = document.getElementById('toast');
                toast.classList.add('show');
                setTimeout(() => toast.classList.remove('show'), 2500);
            }});
        }}
    </script>
</body>
</html>
"""

CARD_TEMPLATE = """
        <div class="card">
            <div class="card-image-wrapper">
                <img src="images/{image_filename}" alt="Doodle">
            </div>
            <div class="card-content">
                <div class="card-header">
                    <span class="date">{date}</span>
                    <span class="pillar-badge">{pillar}</span>
                </div>
                <div class="caption">{caption}</div>
                <div class="actions">
                    <button class="btn-copy" onclick="copyText(this, `{escaped_caption}`)">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                        Copy
                    </button>
                    <a href="images/{image_filename}" download="{image_filename}" class="btn-download">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                        Save
                    </a>
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
        
        if meta_file.exists() and caption_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            with open(caption_file, 'r', encoding='utf-8') as f:
                caption = f.read().strip()
            img_path = Path(meta['image'])
        else:
            img_path = None
            for p in folder.glob("*.png"):
                img_path = p
                break
            if not img_path:
                continue
            caption = caption_file.read_text(encoding='utf-8').strip() if caption_file.exists() else "Test generation."
            meta = {"date": folder.name, "pillar": "测试"}

        if not img_path or not img_path.exists():
            continue

        img_filename = f"{folder.name}_{img_path.name}"
        target_img = IMG_OUTPUT_DIR / img_filename
        shutil.copy2(img_path, target_img)
        
        escaped_caption = caption.replace('`', '\\`').replace('$', '\\$')
        
        card = CARD_TEMPLATE.format(
            image_filename=img_filename,
            date=meta['date'],
            pillar=meta.get('pillar', 'Generated'),
            caption=caption,
            escaped_caption=escaped_caption
        )
        cards_html.append(card)
        
    final_html = HTML_TEMPLATE.format(cards="\n".join(cards_html))
    
    index_file = DOCS_DIR / "index.html"
    index_file.write_text(final_html, encoding='utf-8')
    print(f"✅ Website built successfully at {index_file}")

if __name__ == "__main__":
    build()
