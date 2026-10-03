#!/usr/bin/env python3
"""Build one This Week in AI edition from an edition JSON file and two images.

Reads edition.json (schema in tools/EDITION-SCHEMA.md), copies the hero and
Magnum images into assets/YYYY-MM-DD/, writes the dated issue page with the
structure of the 23 August 2026 edition in the
Magnum AI house style (29 September 2026), and sets the 1200x630 preview.

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

CSS = """    :root { --paper:#FBFBF9; --paper-2:#FFFFFF; --navy:#1F2A37; --ink:#1E1B17; --body:#2B2823; --char:#3A3630; --mute:#63615C; --rust:#EF4029; --coral-text:#C63A2A; --coral-bright:#FF6F5E; --tint:#FBE1D8; --on-navy:#F4F1EA; --on-navy-mute:#C8CDD3; --hair:#DADAD5; --display:'Oswald','Arial Narrow','Liberation Sans Narrow',sans-serif; --sans:'IBM Plex Sans',Arial,system-ui,sans-serif; --mono:'IBM Plex Mono',ui-monospace,'Courier New',monospace; color-scheme:light; }
    *,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }
    html,body { background:#FBFBF9; color-scheme:light; }
    body { color:var(--body); font-family:var(--sans); font-size:17px; line-height:1.65; -webkit-font-smoothing:antialiased; -webkit-text-size-adjust:100%; overflow-wrap:break-word; }
    .page { max-width:720px; margin:0 auto; background:#FBFBF9; }
    .masthead { background:var(--navy); color:var(--on-navy); border-bottom:4px solid var(--coral-bright); padding:26px 28px 28px; }
    .masthead-meta { display:flex; justify-content:space-between; gap:16px; flex-wrap:wrap; }
    .masthead-meta span { color:var(--coral-bright); font-family:var(--mono); font-size:12px; font-weight:500; letter-spacing:.22em; text-transform:uppercase; }
    .masthead-meta span + span { color:var(--on-navy-mute); }
    .masthead-title { margin-top:14px; color:var(--on-navy); font-family:var(--display); font-size:44px; font-weight:700; line-height:.95; text-transform:uppercase; }
    .hero-img,.magnum-img,.magnum-video { display:block; width:100%; height:auto; }
    .content { padding:36px 28px 0; }
    .date-line { margin-bottom:24px; color:var(--coral-text); font-family:var(--mono); font-size:12px; font-weight:500; letter-spacing:.22em; text-transform:uppercase; }
    .opener-block { margin-bottom:44px; padding:22px 26px; background:var(--paper-2); border:2px solid var(--ink); }
    .opener-text { margin-bottom:16px; color:var(--char); font-size:17px; font-style:italic; line-height:1.7; }
    .opener-text:last-of-type { margin-bottom:24px; }
    .index-label { display:flex; align-items:center; gap:12px; margin-bottom:12px; color:var(--coral-text); font-family:var(--mono); font-size:12px; letter-spacing:.22em; text-transform:uppercase; }
    .index-label::after { content:""; flex:1; height:1px; background:var(--ink); }
    .index-list { list-style:none; }
    .index-list li { position:relative; padding-left:18px; color:var(--char); font-size:15.5px; line-height:1.6; margin-bottom:8px; }
    .index-list li::before { content:'\\00B7'; position:absolute; left:2px; color:var(--rust); font-weight:700; }
    .section { padding:0 0 48px; }
    .section-label { display:flex; align-items:center; gap:12px; margin-bottom:14px; color:var(--coral-text); font-family:var(--mono); font-size:12px; font-weight:500; letter-spacing:.22em; text-transform:uppercase; }
    .section-label::after { content:""; flex:1; height:1px; background:var(--ink); }
    .section-headline { margin-bottom:20px; color:var(--ink); font-family:var(--display); font-size:34px; font-weight:600; line-height:1.05; text-transform:uppercase; }
    .section-headline em { font-style:normal; color:var(--rust); }
    .body-text p { margin-bottom:16px; color:var(--body); font-size:17px; line-height:1.7; }
    .body-text p:last-child { margin-bottom:0; }
    .tool-link { display:inline-block; min-height:44px; margin-top:20px; color:var(--coral-text); font-size:15.5px; font-weight:600; line-height:44px; text-decoration:underline; text-decoration-thickness:1px; text-underline-offset:4px; overflow-wrap:anywhere; }
    .tool-link:hover { color:var(--ink); }
    .prompt-label { margin:24px 0 10px; color:var(--coral-text); font-family:var(--mono); font-size:12px; font-weight:500; letter-spacing:.22em; text-transform:uppercase; }
    .prompt-box { margin:0 0 20px; padding:18px 20px; overflow-wrap:anywhere; background:var(--paper-2); border:2px solid var(--ink); }
    .prompt-box pre { margin:0; color:var(--char); font-family:var(--mono); font-size:13px; line-height:1.75; white-space:pre-wrap; word-break:break-word; }
    .prompt-use,.magnum-take { color:var(--char); font-size:15.5px; line-height:1.7; }
    .prompt-use strong,.magnum-take strong { color:var(--coral-text); font-family:var(--mono); font-size:12px; font-weight:500; letter-spacing:.22em; text-transform:uppercase; }
    .magnum-img,.magnum-video { margin:0 0 18px; border:2px solid var(--ink); background:var(--paper-2); }
    .magnum-take { padding-top:14px; border-top:1px solid var(--hair); }
    .signoff { margin:0 28px; padding:36px 0 44px; border-top:2px solid var(--ink); }
    .signoff-body { margin-bottom:16px; color:var(--body); font-size:17px; line-height:1.7; }
    .signoff-details { margin-top:22px; color:var(--mute); font-family:var(--mono); font-size:12px; letter-spacing:.18em; line-height:2; text-transform:uppercase; }
    .signoff-details a { color:var(--coral-text); text-decoration:none; }
    .signoff-details a:hover { text-decoration:underline; }
    .footer { padding:22px 28px; background:var(--navy); text-align:center; }
    .footer p { color:var(--on-navy-mute); font-family:var(--mono); font-size:11px; letter-spacing:.18em; line-height:1.7; text-transform:uppercase; }
    .footer a { color:var(--on-navy); }
    @media (max-width:600px) {
      .masthead { padding:20px 20px 22px; }
      .masthead-meta { flex-direction:column; gap:4px; }
      .masthead-title { font-size:36px; }
      .content { padding:30px 20px 0; }
      .opener-block { padding:18px 18px; }
      .section { padding-bottom:40px; }
      .section-headline { font-size:28px; }
      .prompt-box { padding:14px 14px; }
      .prompt-box pre { font-size:12px; line-height:1.7; }
      .signoff { margin:0 20px; padding:32px 0 36px; }
    }
    @media print {
      html,body { background:#fff; }
      .masthead,.footer { -webkit-print-color-adjust:exact; print-color-adjust:exact; }
      .prompt-box { break-inside:avoid; }
    }"""


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def attr(text: str) -> str:
    return html.escape(text, quote=True)


# Every heading carries one coral word (Magnum AI house style). An optional
# per-section "accent" key names the word; otherwise the longest word that is
# not a filler word is chosen. Purely presentational: the heading text itself
# is unchanged.
ACCENT_SKIP = {
    "about", "after", "again", "against", "always", "because", "before", "being", "between", "could",
    "doesn't", "every", "first", "from", "have", "into", "isn't", "just", "nobody", "nothing", "other",
    "really", "should", "something", "still", "that", "their", "there", "these", "they", "this", "those",
    "through", "until", "what", "when", "where", "which", "while", "with", "without", "would", "your",
}


def accent_heading(text: str, accent: str | None = None) -> str:
    words = list(re.finditer(r"[A-Za-z0-9][A-Za-z0-9'\u2019-]*", text))
    if not words:
        return esc(text)
    pick = None
    if accent:
        pick = next((w for w in words if w.group(0).lower() == accent.lower()), None)
    if pick is None:
        def score(w: re.Match) -> int:
            word = w.group(0).lower()
            bare = re.sub(r"['\u2019]s$", "", word)
            return -1 if word in ACCENT_SKIP or len(words) > 1 and len(bare) < 3 else len(bare)
        best = max(score(w) for w in words)
        pick = next(w for w in words if score(w) == best)
    a, b = pick.span()
    return f"{esc(text[:a])}<em>{esc(text[a:b])}</em>{esc(text[b:])}"


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
        f'        <{tag} class="section-headline">{accent_heading(s["headline"], s.get("accent"))}</{tag}>',
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
        video_prompt = s.get("video_prompt")
        out += [
            f'        <p class="prompt-label">{"The image prompt" if video_prompt else "Prompt"}</p>',
            f'        <div class="prompt-box"><pre>{esc(s["prompt"])}</pre></div>',
        ]
        if video_prompt:
            out += [
                '        <p class="prompt-label">The video prompt</p>',
                f'        <div class="prompt-box"><pre>{esc(video_prompt)}</pre></div>',
            ]
        if s.get("video_url"):
            out.append(
                f'        <video class="magnum-video" controls preload="metadata" '
                f'aria-label="{attr(s["image_alt"])}"><source src="{attr(s["video_url"])}" '
                f'type="video/mp4" /></video>'
            )
        else:
            out.append(f'        <img class="magnum-img" src="{magnum_url}" alt="{attr(s["image_alt"])}" />')
        out.append(f'        <p class="magnum-take">Take from it:<br />{esc(s["take"])}</p>')
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
<html lang="en" style="background:#FBFBF9;">
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
  <meta name="color-scheme" content="light" />
  <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&amp;family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&amp;family=IBM+Plex+Mono:wght@400;500&amp;display=swap" rel="stylesheet" />
  <style>
{CSS}
  </style>
</head>
<body style="background:#FBFBF9;">
  <main class="page">
    <header class="masthead">
      <div class="masthead-meta"><span>Magnum AI &middot; Client Edition</span><span>magnumai.com.au</span></div>
      <p class="masthead-title">This Week in AI</p>
    </header>
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
    parser.add_argument("--magnum", type=Path, help="Magnum image (not needed when the edition's Magnum section already carries a video_url)")
    parser.add_argument("--magnum-video", type=Path, help="Local video file to self-host as the Magnum video; copied into assets/<date>/ and overrides any video_url already in edition.json")
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
    magnum_section = next(s for s in data["sections"] if s["label"] == "The Magnum")
    has_video = args.magnum_video is not None or bool(magnum_section.get("video_url"))
    if not has_video and args.magnum is None:
        raise ValueError("--magnum is required when the Magnum section has no video_url and no --magnum-video")
    required = [args.hero]
    if args.magnum_video is not None:
        required.append(args.magnum_video)
    elif not magnum_section.get("video_url"):
        required.append(args.magnum)
    for p in required:
        if not p.is_file():
            raise FileNotFoundError(p)

    asset_dir = repo / "assets" / d
    asset_dir.mkdir(parents=True, exist_ok=True)
    standing_hero = repo / "assets" / "standing" / "hero.png"
    hero_name = f"newsletter-hero-{d}{args.hero.suffix.lower()}"
    copies = []
    if args.hero.resolve() == standing_hero.resolve():
        hero_url = f"{BASE_URL}/assets/standing/hero.png"
    else:
        copies.append((args.hero, asset_dir / hero_name))
        hero_url = f"{BASE_URL}/assets/{d}/{hero_name}"
    if args.magnum_video is not None:
        magnum_video_name = f"the-magnum-{d}{args.magnum_video.suffix.lower()}"
        copies.append((args.magnum_video, asset_dir / magnum_video_name))
        magnum_section["video_url"] = f"{BASE_URL}/assets/{d}/{magnum_video_name}"
        magnum_url = ""  # unused; the video renders straight from video_url
    elif has_video:
        magnum_url = ""  # unused; the video renders straight from the video_url already in edition.json
    else:
        magnum_name = f"the-magnum-{d}{args.magnum.suffix.lower()}"
        copies.append((args.magnum, asset_dir / magnum_name))
        magnum_url = f"{BASE_URL}/assets/{d}/{magnum_name}"
    for src, dest in copies:
        if src.resolve() != dest.resolve():
            shutil.copy2(src, dest)

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
