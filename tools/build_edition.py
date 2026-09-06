#!/usr/bin/env python3
"""Build one This Week in AI edition from an edition JSON file and two images.

Reads edition.json (schema in tools/EDITION-SCHEMA.md), copies the hero and
Magnum images into assets/YYYY-MM-DD/, writes the dated issue page with the
structure of the 23 August 2026 edition, and sets the 1200x630 preview.

The hero and the preview are standing images (assets/standing/hero.png and
assets/standing/preview.jpg, the same every edition) unless --hero or
--preview is given. The Magnum image is the only one that changes weekly.
It does not touch index.html, issues.json or git. Publishing is the job of
tools/publish_weekly_issue.py, which validates and pushes.

Usage:
    python3 tools/build_edition.py \
        --edition /path/to/edition.json \
        --magnum /path/to/magnum.png \
        [--hero /path/to/hero.png] [--preview /path/to/preview.jpg] \
        --repo /home/user/magnum-newsletter \
        [--out /path/for/finished.html] [--check]

--check runs the same validation the publisher runs and exits 1 on failure,
so copy problems are caught before anything is committed.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

BASE_URL = "https://webes77.github.io/magnum-newsletter"
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
STALE_RE = re.compile(r"\b(last week|this week|yesterday|earlier today|prior edition|previous issue)\b", re.I)
EM_DASH = "—"

REQUIRED_TOP = ("date", "display_date", "title", "dek", "hero_alt", "opener", "index", "sections", "signoff")
SECTION_ORDER = ("The Newsline", "Looking Sideways", "The Win", "Tool of the Week", "Prompt of the Week", "The Magnum")

CSS = """    :root { --cream:#FFFDF7; --stone:#E8E6E3; --gold:#C9A84C; --charcoal:#1A1A1A; --muted:#6B6560; --prompt:#F5F5F0; }
    *,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }
    body { background:var(--stone); color:var(--charcoal); font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif; font-size:17px; line-height:1.75; -webkit-font-smoothing:antialiased; -webkit-text-size-adjust:100%; }
    .page { max-width:680px; margin:0 auto; background:var(--cream); box-shadow:0 0 36px rgba(0,0,0,.05); }
    .top-bar { display:flex; justify-content:space-between; gap:16px; align-items:center; padding:12px 20px; background:#0D0D0D; }
    .top-bar span { color:var(--gold); font-size:10px; letter-spacing:.15em; text-transform:uppercase; }
    .hero-img,.magnum-img { display:block; width:100%; height:auto; }
    .content { padding:36px 24px 0; }
    .date-line { margin-bottom:24px; color:var(--gold); font-size:11px; font-weight:600; letter-spacing:.14em; text-transform:uppercase; }
    .opener-block { margin-bottom:40px; padding:4px 0 4px 18px; border-left:3px solid rgba(201,168,76,.65); }
    .opener-text { margin-bottom:18px; color:#3A3530; font-size:17px; font-style:italic; line-height:1.75; }
    .opener-text:last-of-type { margin-bottom:24px; }
    .index-label { margin-bottom:10px; color:#8A837E; font-size:10px; letter-spacing:.12em; text-transform:uppercase; }
    .index-list { list-style:none; }
    .index-list li { position:relative; padding-left:16px; color:#3A3530; font-size:15px; line-height:1.75; margin-bottom:7px; }
    .index-list li::before { content:'\\00B7'; position:absolute; left:0; color:var(--gold); font-weight:700; }
    .section { padding:40px 0; border-top:1px solid rgba(201,168,76,.5); }
    .section-label { margin-bottom:8px; color:var(--gold); font-family:'Bebas Neue',sans-serif; font-size:13px; letter-spacing:.22em; text-transform:uppercase; }
    .section-headline { margin-bottom:20px; color:#1C1C1E; font-family:'Playfair Display',Georgia,serif; font-size:28px; font-weight:700; line-height:1.2; }
    .body-text p { margin-bottom:18px; color:#1C1C1E; font-size:17px; line-height:1.82; }
    .body-text p:last-child { margin-bottom:0; }
    .tool-link { display:inline-block; min-height:44px; margin-top:20px; color:var(--gold); font-size:15px; font-weight:600; line-height:44px; text-decoration:none; border-bottom:1px solid rgba(201,168,76,.55); }
    .prompt-label { margin:0 0 10px; color:#8A837E; font-size:10px; font-weight:600; letter-spacing:.12em; text-transform:uppercase; }
    .prompt-box { margin:0 0 20px; padding:16px; overflow-wrap:anywhere; background:var(--prompt); border:1px solid rgba(201,168,76,.3); border-left:3px solid var(--gold); border-radius:4px; }
    .prompt-box pre { margin:0; color:#2A2520; font-family:'Courier New',Courier,monospace; font-size:13px; line-height:1.85; white-space:pre-wrap; word-break:break-word; }
    .prompt-use,.magnum-take { color:#3A3530; font-size:14px; line-height:1.8; }
    .prompt-use strong { color:var(--gold); }
    .magnum-img { margin:0 0 16px; border-radius:4px; }
    .magnum-take { padding-top:14px; color:var(--muted); font-style:italic; border-top:1px solid rgba(201,168,76,.25); }
    .signoff { padding:36px 24px 40px; border-top:1px solid rgba(201,168,76,.5); }
    .signoff-body { margin-bottom:20px; color:#2A2520; font-size:17px; line-height:1.85; }
    .signoff-details { color:var(--muted); font-size:13px; line-height:2; }
    .signoff-details a,.footer a { color:var(--gold); text-decoration:none; }
    .footer { padding:16px 24px; background:#0D0D0D; text-align:center; }
    .footer p { color:#8A837E; font-size:11px; letter-spacing:.04em; line-height:1.6; }
    @media (max-width:600px) {
      .top-bar { flex-direction:column; gap:4px; text-align:center; }
      .content { padding:30px 20px 0; }
      .section { padding:34px 0; }
      .section-headline { font-size:24px; }
      .prompt-box pre { font-size:12px; line-height:1.8; }
      .signoff { padding:32px 20px 36px; }
    }"""


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def attr(text: str) -> str:
    return html.escape(text, quote=True)


def paragraphs(items: list[str], cls: str | None = None) -> str:
    c = f' class="{cls}"' if cls else ""
    return "\n".join(f"          <p{c}>{esc(p)}</p>" for p in items)


def load_edition(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED_TOP if k not in data]
    if missing:
        raise ValueError(f"edition.json is missing: {', '.join(missing)}")
    date.fromisoformat(data["date"])
    labels = [s["label"] for s in data["sections"]]
    for label in labels:
        if label not in SECTION_ORDER:
            raise ValueError(f"unknown section label: {label}")
    if labels != [l for l in SECTION_ORDER if l in labels]:
        raise ValueError(f"sections out of order; expected the order {', '.join(SECTION_ORDER)}")
    for must in ("The Newsline", "Tool of the Week", "Prompt of the Week", "The Magnum"):
        if must not in labels:
            raise ValueError(f"required section missing: {must}")
    return data


def render_section(s: dict, magnum_url: str) -> str:
    label = s["label"]
    tag = "h1" if label == "The Newsline" else "h2"
    out = [
        '      <section class="section">',
        f'        <p class="section-label">{esc(label)}</p>',
        f'        <{tag} class="section-headline">{esc(s["headline"])}</{tag}>',
        '        <div class="body-text">',
        paragraphs(s.get("paragraphs", [])),
        "        </div>",
    ]
    if label == "Tool of the Week":
        link = s["link"]
        out.append(f'        <a class="tool-link" href="{attr(link["url"])}">{esc(link["text"])}</a>')
    if label == "Prompt of the Week":
        out += [
            '        <p class="prompt-label">Prompt</p>',
            f'        <div class="prompt-box"><pre>{esc(s["prompt"])}</pre></div>',
            '        <div class="body-text">',
            '          <p class="prompt-use"><strong>Use it for</strong><br />' + "<br />".join(esc(u) for u in s["use"]) + "</p>",
            "        </div>",
        ]
    if label == "The Magnum":
        out += [
            '        <p class="prompt-label">Prompt</p>',
            f'        <div class="prompt-box"><pre>{esc(s["prompt"])}</pre></div>',
            f'        <img class="magnum-img" src="{magnum_url}" alt="{attr(s["image_alt"])}" />',
            f'        <p class="magnum-take">Take from it:<br />{esc(s["take"])}</p>',
        ]
    out.append("      </section>")
    return "\n".join(out)


def render(data: dict, hero_url: str, magnum_url: str) -> str:
    d = data["date"]
    issue_url = f"{BASE_URL}/issues/{d}.html"
    preview_url = f"{BASE_URL}/assets/previews/{d}.jpg"
    full_title = f"This Week in AI, {data['display_date']} | {data['title']} | Magnum AI"
    index_items = "\n".join(
        f'          <li>{esc(i["label"])} &middot; {esc(i["line"])}</li>' for i in data["index"]
    )
    sections = "\n\n".join(render_section(s, magnum_url) for s in data["sections"])
    signoff = "\n".join(f'      <p class="signoff-body">{esc(p)}</p>' for p in data["signoff"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0" />
  <meta name="format-detection" content="telephone=no" />
  <title>{esc(full_title)}</title>
  <meta name="description" content="{attr(data['dek'])}" />
  <link rel="canonical" href="{issue_url}" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{issue_url}" />
  <meta property="og:title" content="{attr(full_title)}" />
  <meta property="og:description" content="{attr(data['dek'])}" />
  <meta property="og:image" content="{preview_url}" />
  <meta property="og:image:secure_url" content="{preview_url}" />
  <meta property="og:image:type" content="image/jpeg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="{attr(data['hero_alt'])}" />
  <meta property="og:site_name" content="Magnum AI" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{attr(full_title)}" />
  <meta name="twitter:description" content="{attr(data['dek'])}" />
  <meta name="twitter:image" content="{preview_url}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&amp;family=Playfair+Display:wght@400;700&amp;family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet" />
  <style>
{CSS}
  </style>
</head>
<body>
  <main class="page">
    <div class="top-bar"><span>Magnum AI &middot; Client Edition</span><span>magnumai.com.au</span></div>
    <img class="hero-img" src="{hero_url}" alt="{attr(data['hero_alt'])}" />
    <div class="content">
      <p class="date-line">{esc(data['display_date'])}</p>
      <div class="opener-block">
{paragraphs(data['opener'], 'opener-text').replace('          <p', '        <p')}
        <p class="index-label">In this edition:</p>
        <ul class="index-list">
{index_items}
        </ul>
      </div>

{sections}
    </div>
    <div class="signoff">
{signoff}
      <p class="signoff-details">Magnum AI | <a href="https://magnumai.com.au">magnumai.com.au</a></p>
    </div>
    <footer class="footer"><p>You're getting this because you're a Magnum AI client.</p></footer>
  </main>
</body>
</html>
"""


def check(page: str, data: dict) -> list[str]:
    """The publisher's validation, plus the house rules, run before anything is committed."""
    errors: list[str] = []
    d = data["date"]
    if PLACEHOLDER_RE.search(page):
        errors.append("unresolved {{PLACEHOLDER}} marker")
    body = re.search(r"<body\b[^>]*>(.*?)</body>", page, re.I | re.S)
    text = body.group(1) if body else page
    text = re.sub(r'<div\b[^>]*class="[^"]*\bprompt-box\b[^"]*"[^>]*>.*?</div>', " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text).replace("This Week in AI", "")
    m = STALE_RE.search(text)
    if m:
        errors.append(f"stale relative-time phrase in body copy: '{m.group(0)}' (use the date or 'this edition')")
    if EM_DASH in page:
        errors.append("em dash in the page; use a comma, a full stop or a middot")
    if re.search(r"\bsolid\b", text, re.I):
        errors.append("the word 'solid' is banned")
    if f"{BASE_URL}/issues/{d}.html" not in page:
        errors.append("canonical issue URL missing")
    if f"{BASE_URL}/assets/previews/{d}.jpg" not in page:
        errors.append("preview URL missing")
    return errors


def make_preview(hero: Path, out: Path) -> None:
    from PIL import Image, ImageOps

    out.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(hero) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        preview = ImageOps.fit(image, (1200, 630), method=Image.Resampling.LANCZOS, centering=(0.5, 0.45))
        preview.save(out, "JPEG", quality=88, optimize=True, progressive=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a This Week in AI edition from edition.json")
    parser.add_argument("--edition", required=True, type=Path)
    parser.add_argument("--magnum", required=True, type=Path)
    parser.add_argument("--hero", type=Path, help="Hero image (default: the standing assets/standing/hero.png)")
    parser.add_argument("--preview", type=Path, help="1200x630 JPEG preview (default: the standing assets/standing/preview.jpg; pass 'crop' to crop the hero)")
    parser.add_argument("--repo", type=Path, default=Path("/home/user/magnum-newsletter"))
    parser.add_argument("--out", type=Path, help="Where to write the finished HTML (default: <repo>/build/<date>/finished.html)")
    parser.add_argument("--check", action="store_true", help="Validate and exit 1 on any failure")
    args = parser.parse_args()

    data = load_edition(args.edition)
    d = data["date"]
    repo = args.repo.resolve()
    if args.hero is None:
        args.hero = repo / "assets" / "standing" / "hero.png"
    for p in (args.hero, args.magnum):
        if not p.is_file():
            raise FileNotFoundError(p)

    asset_dir = repo / "assets" / d
    asset_dir.mkdir(parents=True, exist_ok=True)
    standing_hero = repo / "assets" / "standing" / "hero.png"
    hero_name = f"newsletter-hero-{d}{args.hero.suffix.lower()}"
    magnum_name = f"the-magnum-{d}{args.magnum.suffix.lower()}"
    copies = [(args.magnum, asset_dir / magnum_name)]
    if args.hero.resolve() == standing_hero.resolve():
        hero_url = f"{BASE_URL}/assets/standing/hero.png"
    else:
        copies.append((args.hero, asset_dir / hero_name))
        hero_url = f"{BASE_URL}/assets/{d}/{hero_name}"
    for src, dest in copies:
        if src.resolve() != dest.resolve():
            shutil.copy2(src, dest)
    magnum_url = f"{BASE_URL}/assets/{d}/{magnum_name}"

    page = render(data, hero_url, magnum_url)
    out = args.out or (repo / "build" / d / "finished.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    preview = out.parent / "preview.jpg"
    if args.preview is not None and str(args.preview) == "crop":
        make_preview(args.hero, preview)
    else:
        src = args.preview or (repo / "assets" / "standing" / "preview.jpg")
        if not src.is_file():
            raise FileNotFoundError(src)
        shutil.copy2(src, preview)
        from PIL import Image
        with Image.open(preview) as im:
            if im.size != (1200, 630) or im.format != "JPEG":
                raise ValueError(f"preview must be a 1200x630 JPEG; got {im.size} {im.format}")

    errors = check(page, data)
    print(f"Written: {out}")
    print(f"Preview: {preview}")
    print(f"Assets:  {asset_dir}")
    if errors:
        print("CHECK FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1 if args.check else 0
    print("CHECK PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
