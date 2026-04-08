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
    <title>@BingBang Daily Creations</title>
    <style>
        :root {{
            --bg-color: #f8f8f8;
            --card-bg: #ffffff;
            --text-main: #333333;
            --text-sub: #666666;
            --xhs-red: #ff2442;
            --radius: 12px;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            margin: 0;
            padding: 20px;
            color: var(--text-main);
        }}
        header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        header p {{
            color: var(--text-sub);
            font-size: 14px;
            margin-top: 8px;
        }}
        .masonry {{
            columns: 1;
            column-gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        @media (min-width: 600px) {{ .masonry {{ columns: 2; }} }}
        @media (min-width: 900px) {{ .masonry {{ columns: 3; }} }}
        @media (min-width: 1200px) {{ .masonry {{ columns: 4; }} }}
        
        .card {{
            background: var(--card-bg);
            border-radius: var(--radius);
            margin-bottom: 20px;
            break-inside: avoid;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            overflow: hidden;
            transition: transform 0.2s;
            display: flex;
            flex-direction: column;
        }}
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.1);
        }}
        .card-image-wrapper {{
            position: relative;
            width: 100%;
            padding-top: 100%; /* 1:1 Aspect Ratio */
        }}
        .card img {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-bottom: 1px solid #f0f0f0;
        }}
        .card-content {{
            padding: 16px;
        }}
        .date-badge {{
            display: inline-block;
            background: #f0f0f0;
            color: var(--text-sub);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-bottom: 12px;
            font-weight: 500;
        }}
        .caption {{
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 16px;
            white-space: pre-wrap;
        }}
        .actions {{
            display: flex;
            gap: 10px;
            margin-top: auto;
        }}
        button {{
            flex: 1;
            padding: 8px 12px;
            border: none;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: opacity 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }}
        button:hover {{
            opacity: 0.8;
        }}
        .btn-copy {{
            background-color: #f0f0f0;
            color: var(--text-main);
        }}
        .btn-download {{
            background-color: var(--xhs-red);
            color: white;
            text-decoration: none;
        }}
        .toast {{
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 14px;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s;
            z-index: 1000;
        }}
        .toast.show {{
            opacity: 1;
        }}
    </style>
</head>
<body>

    <header>
        <h1>@BingBang Content Gallery</h1>
        <p>Daily generated doodle art & captions for Xiaohongshu</p>
    </header>

    <div class="masonry">
        {cards}
    </div>

    <div id="toast" class="toast">Copied to clipboard!</div>

    <script>
        function copyText(button, text) {{
            navigator.clipboard.writeText(text).then(() => {{
                const toast = document.getElementById('toast');
                toast.classList.add('show');
                setTimeout(() => toast.classList.remove('show'), 2000);
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
                <div class="date-badge">{date} • {pillar}</div>
                <div class="caption">{caption}</div>
                <div class="actions">
                    <button class="btn-copy" onclick="copyText(this, `{escaped_caption}`)">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                        Copy
                    </button>
                    <a href="images/{image_filename}" download="{image_filename}" class="btn-download" style="text-decoration: none; display: flex; box-sizing: border-box;">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                        Save
                    </a>
                </div>
            </div>
        </div>
"""

def build():
    cards_html = []
    
    # Get all draft folders sorted by date descending
    if not DRAFTS_DIR.exists():
        print("No drafts directory found.")
        return
        
    date_folders = sorted([d for d in DRAFTS_DIR.iterdir() if d.is_dir() and d.name != "samples"], reverse=True)
    
    for folder in date_folders:
        meta_file = folder / "metadata.json"
        caption_file = folder / "caption.md"
        
        # Check if it's the standard format or the weird/warm tests
        if meta_file.exists() and caption_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            with open(caption_file, 'r', encoding='utf-8') as f:
                caption = f.read().strip()
                
            img_path = Path(meta['image'])
        else:
            # Look for test images as fallback
            img_path = None
            for p in folder.glob("*.png"):
                img_path = p
                break
                
            if not img_path:
                continue
                
            caption = caption_file.read_text(encoding='utf-8').strip() if caption_file.exists() else "Test generation."
            meta = {
                "date": folder.name,
                "pillar": "测试 (Test)"
            }

        if not img_path or not img_path.exists():
            continue

        # Copy image to docs/images
        img_filename = f"{folder.name}_{img_path.name}"
        target_img = IMG_OUTPUT_DIR / img_filename
        shutil.copy2(img_path, target_img)
        
        # Escape caption for JS string
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
