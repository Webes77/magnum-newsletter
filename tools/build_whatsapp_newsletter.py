"""
build_whatsapp_newsletter.py
Magnum AI — WhatsApp Newsletter Builder

Usage:
    python3.11 build_whatsapp_newsletter.py \
        --hero /path/to/hero.png \
        --station /path/to/image_station.png \
        --out /path/to/output_dir \
        --date "10 May 2026"

Outputs:
    {out}/magnum_ai_newsletter_{DDMMMYYYY}_whatsapp.html   (self-contained, base64 images)
    {out}/hero_b64.txt                                      (cached for rebuild speed)
    {out}/station_b64.txt

The script does NOT push to GitHub — that step is handled separately via gh CLI.
"""

import argparse
import base64
import html as html_lib
import mimetypes
import pathlib
import re


def encode_image(path: str) -> str:
    return base64.b64encode(pathlib.Path(path).read_bytes()).decode()


def image_mime(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime if mime and mime.startswith("image/") else "image/png"


def slugify_date(date_str: str) -> str:
    """Convert '10 May 2026' -> '10may2026'"""
    return re.sub(r"\s+", "", date_str).lower()


def build(hero_path, station_path, out_dir, date_str, title, description, og_url, preview_url):
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Cache b64 to speed up rebuilds
    hero_cache = out / "hero_b64.txt"
    station_cache = out / "station_b64.txt"

    if not hero_cache.exists():
        print("Encoding hero image...")
        hero_cache.write_text(encode_image(hero_path))
    if not station_cache.exists():
        print("Encoding image station...")
        station_cache.write_text(encode_image(station_path))

    hero_src = f"data:{image_mime(hero_path)};base64,{hero_cache.read_text().strip()}"
    station_src = f"data:{image_mime(station_path)};base64,{station_cache.read_text().strip()}"

    safe_title = html_lib.escape(title, quote=True)
    safe_description = html_lib.escape(description, quote=True)
    safe_og_url = html_lib.escape(og_url, quote=True)
    safe_preview_url = html_lib.escape(preview_url, quote=True)

    # ── TEMPLATE ─────────────────────────────────────────────────────────────
    # Replace {{PLACEHOLDER}} values below with each issue's content.
    # Sections are clearly labelled — only edit the content between the markers.
    # ─────────────────────────────────────────────────────────────────────────

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0" />
  <meta name="format-detection" content="telephone=no" />
  <title>{safe_title} | Magnum AI</title>
  <link rel="canonical" href="{safe_og_url}" />

  <!-- Open Graph / WhatsApp preview -->
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{safe_og_url}" />
  <meta property="og:title" content="{safe_title} | Magnum AI" />
  <meta property="og:description" content="{safe_description}" />
  <meta property="og:image" content="{safe_preview_url}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:site_name" content="Magnum AI" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{safe_title} | Magnum AI" />
  <meta name="twitter:description" content="{safe_description}" />
  <meta name="twitter:image" content="{safe_preview_url}" />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Playfair+Display:wght@400;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background-color: #E8E6E3; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; color: #1A1A1A; font-size: 17px; line-height: 1.75; -webkit-font-smoothing: antialiased; -webkit-text-size-adjust: 100%; }}
    .page {{ max-width: 680px; margin: 0 auto; background-color: #FFFDF7; }}
    .top-bar {{ background-color: #0D0D0D; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; }}
    .top-bar span {{ font-family: 'Inter', sans-serif; font-size: 10px; letter-spacing: 0.15em; color: #D4AF37; text-transform: uppercase; }}
    .hero-img {{ width: 100%; display: block; }}
    .content {{ padding: 36px 24px 0; }}
    .date-line {{ font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 0.14em; color: #D4AF37; text-transform: uppercase; font-weight: 600; margin-bottom: 24px; }}
    .opener-block {{ border-left: 3px solid rgba(212,175,55,0.6); padding: 4px 0 4px 18px; margin-bottom: 40px; }}
    .opener-text {{ font-size: 18px; line-height: 1.8; color: #3A3530; font-style: italic; margin-bottom: 20px; }}
    .index-label {{ font-family: 'Inter', sans-serif; font-size: 10px; letter-spacing: 0.12em; color: #9B9490; text-transform: uppercase; margin-bottom: 10px; }}
    .index-list {{ list-style: none; padding: 0; }}
    .index-list li {{ font-size: 15px; line-height: 2; color: #3A3530; padding-left: 16px; position: relative; }}
    .index-list li::before {{ content: "-"; position: absolute; left: 0; color: #D4AF37; font-weight: 600; }}
    .gold-rule {{ border: none; border-top: 1px solid rgba(212,175,55,0.5); margin: 0 0 20px; }}
    .section-label {{ font-family: 'Bebas Neue', sans-serif; font-size: 13px; letter-spacing: 0.22em; color: #D4AF37; text-transform: uppercase; margin-bottom: 8px; }}
    .section-headline {{ font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 700; color: #1C1C1E; line-height: 1.2; margin-bottom: 20px; }}
    .section-block {{ padding: 40px 0; }}
    .body-text {{ font-size: 17px; line-height: 1.85; color: #1C1C1E; }}
    .body-text p {{ margin-bottom: 18px; }}
    .body-text p:last-child {{ margin-bottom: 0; }}
    .news-item {{ margin-top: 28px; padding-top: 28px; border-top: 1px solid rgba(212,175,55,0.2); }}
    .news-item:first-child {{ margin-top: 0; padding-top: 0; border-top: none; }}
    .news-headline {{ font-family: 'Playfair Display', serif; font-size: 21px; font-weight: 700; color: #1C1C1E; line-height: 1.3; margin-bottom: 14px; }}
    .tool-link {{ display: inline-block; margin-top: 18px; font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 600; color: #D4AF37; letter-spacing: 0.04em; text-decoration: none; border-bottom: 1px solid rgba(212,175,55,0.5); padding-bottom: 3px; min-height: 44px; line-height: 44px; }}
    .prompt-setup {{ font-size: 15px; line-height: 1.8; color: #3A3530; font-style: italic; margin-bottom: 20px; }}
    .prompt-box {{ background-color: rgba(212,175,55,0.05); border: 1px solid rgba(212,175,55,0.3); border-left: 3px solid #D4AF37; border-radius: 4px; padding: 20px 22px; margin: 0 0 20px; }}
    .prompt-box p {{ font-family: 'Courier New', Courier, monospace; font-size: 13px; line-height: 1.9; color: #2A2520; margin: 0 0 14px; }}
    .prompt-box p:last-child {{ margin-bottom: 0; }}
    .prompt-use {{ font-size: 14px; line-height: 1.8; color: #3A3530; }}
    .prompt-use strong {{ color: #D4AF37; }}
    .station-intro {{ font-size: 17px; line-height: 1.85; color: #1C1C1E; margin-bottom: 20px; }}
    .station-intro a {{ color: #D4AF37; text-decoration: none; border-bottom: 1px solid rgba(212,175,55,0.4); }}
    .station-img {{ width: 100%; display: block; margin-top: 28px; border-radius: 3px; }}
    .station-caption {{ font-size: 14px; line-height: 1.75; color: #6B6560; font-style: italic; margin-top: 16px; padding-top: 14px; border-top: 1px solid rgba(212,175,55,0.2); }}
    .signoff {{ padding: 36px 24px 40px; border-top: 1px solid rgba(212,175,55,0.4); }}
    .signoff-body {{ font-size: 17px; line-height: 1.85; color: #2A2520; margin-bottom: 20px; }}
    .signoff-name {{ font-family: 'Playfair Display', serif; font-weight: 700; font-size: 18px; color: #0D0D0D; margin-bottom: 8px; }}
    .signoff-details {{ font-size: 13px; color: #6B6560; line-height: 2; }}
    .signoff-details a {{ color: #D4AF37; text-decoration: none; }}
    .footer {{ background-color: #0D0D0D; padding: 16px 24px; text-align: center; }}
    .footer p {{ font-size: 11px; letter-spacing: 0.06em; color: #6B6560; }}
    .footer a {{ color: #D4AF37; text-decoration: none; }}
    @media (max-width: 600px) {{
      .section-headline {{ font-size: 23px; }}
      .news-headline {{ font-size: 19px; }}
      .opener-text {{ font-size: 16px; }}
      .top-bar {{ flex-direction: column; gap: 4px; text-align: center; }}
      .prompt-box {{ padding: 16px 18px; }}
      .prompt-box p {{ font-size: 12px; }}
    }}
  </style>
</head>
<body>
  <div class="page">

    <div class="top-bar">
      <span>Magnum AI &mdash; Client Edition</span>
      <span>magnumai.com.au</span>
    </div>

    <img class="hero-img" src="{hero_src}" alt="Magnum AI Newsletter" />

    <div class="content">
      <p class="date-line">{date_str} &nbsp;&middot;&nbsp; Weekly Briefing</p>

      <!-- ═══ OPENER ═══ Edit opener_text and index items below ═══ -->
      <div class="opener-block">
        <p class="opener-text">{{OPENER_TEXT}}</p>
        <p class="index-label">In this edition</p>
        <ul class="index-list">
          {{INDEX_ITEMS}}
        </ul>
      </div>

      <!-- ═══ SECTION 1: JAMES'S TAKE ═══ -->
      <hr class="gold-rule" />
      <div class="section-block">
        <p class="section-label">James&rsquo;s Take</p>
        <h2 class="section-headline">{{JAKES_TAKE_HEADLINE}}</h2>
        <div class="body-text">
          {{JAMES_TAKE_BODY}}
        </div>
      </div>

      <!-- ═══ SECTION 2: WHAT'S HAPPENING ═══ -->
      <hr class="gold-rule" />
      <div class="section-block">
        <p class="section-label">What&rsquo;s Happening</p>
        {{NEWS_ITEMS}}
      </div>

      <!-- ═══ SECTION 3: TOOL OF THE WEEK ═══ -->
      <hr class="gold-rule" />
      <div class="section-block">
        <p class="section-label">Tool of the Week</p>
        <h2 class="section-headline">{{TOOL_NAME}}</h2>
        <div class="body-text">
          {{TOOL_BODY}}
        </div>
        <a class="tool-link" href="{{TOOL_URL}}" target="_blank" rel="noopener">{{TOOL_URL_LABEL}} &rarr;</a>
      </div>

      <!-- ═══ SECTION 4: PROMPT OF THE WEEK ═══ -->
      <hr class="gold-rule" />
      <div class="section-block">
        <p class="section-label">Prompt of the Week</p>
        <h2 class="section-headline">{{PROMPT_HEADLINE}}</h2>
        <p class="prompt-setup">{{PROMPT_SETUP}}</p>
        <div class="prompt-box">
          {{PROMPT_PARAGRAPHS}}
        </div>
        <p class="prompt-use"><strong>Use it for:</strong> {{PROMPT_USE}}</p>
      </div>

      <!-- ═══ SECTION 5: IMAGE STATION ═══ -->
      <hr class="gold-rule" />
      <div class="section-block">
        <p class="section-label">Image Station</p>
        <h2 class="section-headline">{{STATION_HEADLINE}}</h2>
        <p class="station-intro">{{STATION_INTRO}}</p>
        <div class="prompt-box">
          {{STATION_PROMPT_PARAGRAPHS}}
        </div>
        <img class="station-img" src="{station_src}" alt="Image Station" />
        <p class="station-caption">{{STATION_CAPTION}}</p>
      </div>

    </div>

    <div class="signoff">
      <p class="signoff-body">Questions about any of this? Reply to this email or reach out directly. If you want to walk through how any of these tools could work in your specific business, that&rsquo;s exactly what I&rsquo;m here for.</p>
      <p class="signoff-body">Speak soon.</p>
      <p class="signoff-name">James</p>
      <p class="signoff-details">Magnum AI &nbsp;&middot;&nbsp; <a href="https://magnumai.com.au">magnumai.com.au</a></p>
    </div>

    <div class="footer">
      <p>Magnum AI &nbsp;&middot;&nbsp; <a href="https://magnumai.com.au">magnumai.com.au</a> &nbsp;&middot;&nbsp; You&rsquo;re getting this because you&rsquo;re a Magnum AI client.</p>
    </div>

  </div>
</body>
</html>"""

    slug = slugify_date(date_str)
    out_file = out / f"magnum_ai_newsletter_{slug}_whatsapp.html"
    out_file.write_text(html, encoding="utf-8")
    print(f"Written: {out_file} ({out_file.stat().st_size / 1024 / 1024:.1f} MB)")
    return str(out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Magnum AI WhatsApp newsletter")
    parser.add_argument("--hero", required=True, help="Path to hero image (PNG)")
    parser.add_argument("--station", required=True, help="Path to image station image (PNG)")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--date", required=True, help="Issue date, e.g. '10 May 2026'")
    parser.add_argument("--title", default="This Week in AI", help="OG title (issue headline)")
    parser.add_argument("--description", default="The Magnum AI weekly client briefing.", help="OG description (one sentence)")
    parser.add_argument("--og-url", required=True, help="Permanent dated issue URL")
    parser.add_argument("--preview-url", required=True, help="Absolute 1200x630 issue preview URL")
    args = parser.parse_args()

    build(
        args.hero,
        args.station,
        args.out,
        args.date,
        args.title,
        args.description,
        args.og_url,
        args.preview_url,
    )
