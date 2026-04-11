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
            --bg-color: #F9F8F6;
            --card-bg: #FFFFFF;
            --text-main: #2C2C2C;
            --text-sub: #8E8E8E;
            --accent: #E85D45;
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
        
        /* Carousel Styles */
        .carousel-container {{
            position: relative;
            width: 100%;
            padding-top: 100%; /* 1:1 Aspect Ratio */
            background: #F4F4F4;
            overflow: hidden;
        }}
        .carousel-track {{
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            display: flex;
            transition: transform 0.3s ease-in-out;
        }}
        .carousel-slide {{
            min-width: 100%;
            height: 100%;
        }}
        .carousel-slide img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .carousel-controls {{
            position: absolute;
            bottom: 12px;
            left: 0;
            width: 100%;
            display: flex;
            justify-content: center;
            gap: 6px;
            z-index: 10;
        }}
        .dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: rgba(0,0,0,0.2);
            cursor: pointer;
            transition: all 0.2s;
        }}
        .dot.active {{
            background: var(--accent);
            transform: scale(1.2);
        }}
        .btn-nav {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255,255,255,0.8);
            border: none;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 10;
            opacity: 0;
            transition: opacity 0.2s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .carousel-container:hover .btn-nav {{
            opacity: 1;
        }}
        .btn-prev {{ left: 12px; }}
        .btn-next {{ right: 12px; }}

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
        function showToast(message) {{
            const toast = document.getElementById('toast');
            toast.innerText = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2500);
        }}

        function copyText(button, text) {{
            navigator.clipboard.writeText(text).then(() => {{
                showToast('Copied! ✨');
            }});
        }}

        // Carousel Logic
        document.querySelectorAll('.carousel-container').forEach(container => {{
            const track = container.querySelector('.carousel-track');
            const slides = container.querySelectorAll('.carousel-slide');
            const dots = container.querySelectorAll('.dot');
            const btnPrev = container.querySelector('.btn-prev');
            const btnNext = container.querySelector('.btn-next');
            const downloadBtn = container.closest('.card').querySelector('.btn-download');
            
            if (slides.length <= 1) return;
            
            let currentIndex = 0;
            const maxIndex = slides.length - 1;

            function updateCarousel() {{
                track.style.transform = `translateX(-${{currentIndex * 100}}%)`;
                dots.forEach((dot, idx) => {{
                    dot.classList.toggle('active', idx === currentIndex);
                }});
                
                // Update download link
                const currentImg = slides[currentIndex].querySelector('img').src;
                const fileName = currentImg.split('/').pop();
                downloadBtn.href = currentImg;
                downloadBtn.download = fileName;
            }}

            if (btnPrev) btnPrev.addEventListener('click', () => {{
                currentIndex = currentIndex > 0 ? currentIndex - 1 : maxIndex;
                updateCarousel();
            }});

            if (btnNext) btnNext.addEventListener('click', () => {{
                currentIndex = currentIndex < maxIndex ? currentIndex + 1 : 0;
                updateCarousel();
            }});

            dots.forEach((dot, idx) => {{
                dot.addEventListener('click', () => {{
                    currentIndex = idx;
                    updateCarousel();
                }});
            }});
            
            // Initial setup
            updateCarousel();
        }});
    </script>
</body>
</html>
"""

CARD_TEMPLATE = """
        <div class="card" data-id="{date}">
            <div class="carousel-container">
                <div class="carousel-track" style="width: {track_width}%;">
                    {slides}
                </div>
                {nav_buttons}
                <div class="carousel-controls">
                    {dots}
                </div>
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
                    <a href="images/{first_image_filename}" download="{first_image_filename}" class="btn-download">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                        Save Current
                    </a>
                </div>
            </div>
        </div>
"""

SLIDE_TEMPLATE = """
                    <div class="carousel-slide">
                        <img src="images/{image_filename}" alt="Doodle">
                    </div>"""

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
        else:
            # Fallback
            caption = caption_file.read_text(encoding='utf-8').strip() if caption_file.exists() else "Test generation."
            meta = {"date": folder.name, "pillar": "测试"}
            images_to_show = list(folder.glob("*.png"))

        # Filter to only existing images
        images_to_show = [img for img in images_to_show if img.exists()]
        
        if not images_to_show:
            continue

        slides_html = ""
        dots_html = ""
        first_img_filename = ""
        
        for idx, img_path in enumerate(images_to_show):
            img_filename = f"{folder.name}_{img_path.name}"
            if idx == 0:
                first_img_filename = img_filename
                
            target_img = IMG_OUTPUT_DIR / img_filename
            shutil.copy2(img_path, target_img)
            
            slides_html += SLIDE_TEMPLATE.format(image_filename=img_filename)
            active_class = 'active' if idx == 0 else ''
            dots_html += f'<div class="dot {active_class}"></div>'
            
        track_width = len(images_to_show) * 100
        
        nav_buttons = ""
        if len(images_to_show) > 1:
            nav_buttons = """
                <button class="btn-nav btn-prev"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"></polyline></svg></button>
                <button class="btn-nav btn-next"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg></button>
            """
        else:
            dots_html = "" # Hide dots if only 1 image
        
        escaped_caption = caption.replace('`', '\\`').replace('$', '\\$')
        
        card = CARD_TEMPLATE.format(
            track_width=track_width,
            slides=slides_html,
            nav_buttons=nav_buttons,
            dots=dots_html,
            first_image_filename=first_img_filename,
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
