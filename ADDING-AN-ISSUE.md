# Publishing a Magnum AI weekly newsletter

GitHub Pages hosts the newsletter at **https://webes77.github.io/magnum-newsletter/**. The root always serves the current edition. Every issue also receives a permanent dated page, while the issue library remains at **https://webes77.github.io/magnum-newsletter/archive.html**.

> **Never replace the root with the archive. Never change a URL after it has been sent to clients.**

## Permanent structure

| Purpose | Repository path | Public URL |
|---|---|---|
| Current newsletter | `index.html` | `https://webes77.github.io/magnum-newsletter/` |
| Newsletter archive | `archive.html` | `https://webes77.github.io/magnum-newsletter/archive.html` |
| Issue manifest | `issues.json` | Loaded by the archive page |
| Permanent edition | `issues/YYYY-MM-DD.html` | `https://webes77.github.io/magnum-newsletter/issues/YYYY-MM-DD.html` |
| WhatsApp preview | `assets/previews/YYYY-MM-DD.jpg` | `https://webes77.github.io/magnum-newsletter/assets/previews/YYYY-MM-DD.jpg` |

## Weekly workflow

### 1. Confirm the inputs

Confirm the publication date, headline, archive summary, complete copy, supplied hero, final image-section image, and image order. The supplied brief controls the design and section sequence. Do not generate or replace images unless James explicitly requests it.

Replace editorial references that age badly, such as “last week”, “yesterday”, or “previous issue”, with exact dates or evergreen wording.

### 2. Build the dated edition

Use the previous edition as the structural reference or run `tools/build_whatsapp_newsletter.py`. Set the issue metadata to its permanent dated URL. Keep supplied images embedded as data URIs and external links absolute.

```bash
python3 tools/build_whatsapp_newsletter.py \
  --hero /path/to/hero.png \
  --station /path/to/final-image.png \
  --out /home/ubuntu/newsletter_DDMMMYYYY/ \
  --date "11 July 2026" \
  --title "Issue headline" \
  --description "One-sentence preview description." \
  --og-url "https://webes77.github.io/magnum-newsletter/issues/2026-07-11.html" \
  --preview-url "https://webes77.github.io/magnum-newsletter/assets/previews/2026-07-11.jpg"
```

Replace every `{{PLACEHOLDER}}`, then perform a complete mobile-page review.

### 3. Create the WhatsApp preview

Create and visually check a deterministic 1200 × 630 JPEG from the exact supplied hero.

```bash
python3 tools/create_og_preview.py \
  --hero /path/to/hero.png \
  --out /home/ubuntu/newsletter_DDMMMYYYY/preview.jpg
```

Do not use generative editing. Use focus controls only when the crop needs reframing.

### 4. Validate

| Check | Required result |
|---|---|
| Placeholders | No unresolved `{{...}}` markers |
| Editorial copy | No stale relative-date references |
| Images | Supplied assets appear in the required order |
| Mobile layout | Complete visual review passes |
| Preview | JPEG is exactly 1200 × 630 and preserves the hero |
| Dated metadata | Canonical, `og:url`, and `og:image` use dated URLs |
| Root metadata | Canonical and `og:url` use the root; `og:image` uses the current preview |
| Archive | `archive.html` remains the issue library and every manifest file exists |

### 5. Publish the complete edition

```bash
python3 tools/publish_weekly_issue.py \
  --html /home/ubuntu/newsletter_DDMMMYYYY/finished.html \
  --preview /home/ubuntu/newsletter_DDMMMYYYY/preview.jpg \
  --date 2026-07-11 \
  --display-date "11 July 2026" \
  --title "Issue headline" \
  --dek "Archive summary." \
  --content "The Newsline — description" \
  --content "The Magnum — description" \
  --push
```

The publisher writes four current-edition files in one commit: `index.html`, the dated issue, the dated preview, and `issues.json`. It never edits `archive.html`. Use `--replace` only when intentionally correcting an existing date.

### 6. Verify the exact public links

Confirm HTTP 200 and correct content at the root, dated issue, preview, and archive. Inspect the public metadata rather than relying on local files.

For a new WhatsApp broadcast, share the dated issue URL first to avoid an older cached preview. Keep the root working as the current newsletter for anyone who already received or bookmarked it. Never say a link is ready until opening that exact public URL shows the intended edition.
