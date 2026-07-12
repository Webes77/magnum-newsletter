# Publishing a Magnum AI weekly newsletter

This repository is the permanent home of the Magnum AI newsletter. GitHub Pages serves the archive at **https://webes77.github.io/magnum-newsletter/**. Every edition receives its own dated page and its own hero-based WhatsApp preview.

> **Do not replace `index.html` with a weekly issue.** The root page is the archive. Publish editions under `issues/YYYY-MM-DD.html` and share that dated URL.

## Permanent structure

| Purpose | Repository path | Public URL |
|---|---|---|
| Newsletter archive | `index.html` | `https://webes77.github.io/magnum-newsletter/` |
| Issue manifest | `issues.json` | Loaded by the archive homepage |
| Weekly edition | `issues/YYYY-MM-DD.html` | `https://webes77.github.io/magnum-newsletter/issues/YYYY-MM-DD.html` |
| WhatsApp preview | `assets/previews/YYYY-MM-DD.jpg` | `https://webes77.github.io/magnum-newsletter/assets/previews/YYYY-MM-DD.jpg` |

## Weekly workflow

### 1. Confirm the inputs

Confirm the publication date, headline, archive summary, complete issue copy, supplied hero, final image-section image, and required image order. The supplied issue brief controls the design and section structure. Do not generate or replace images unless James explicitly requests it.

Audit editorial copy for relative references that age badly, such as “last week”, “yesterday”, or “previous issue”. Use exact dates or evergreen wording. Relative language inside a reusable prompt can remain when it describes the prompt’s behaviour rather than the issue’s publication timing.

### 2. Build the self-contained edition

Use the previous edition as the structural reference or run `tools/build_whatsapp_newsletter.py`. Set the canonical and social metadata to the edition’s dated URLs from the start. Keep supplied newsletter images embedded as data URIs and use absolute URLs for external links.

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

Replace every `{{PLACEHOLDER}}` in the generated HTML. Prompt blocks remain monospace and visually distinct. Perform a full mobile-page review before publishing.

### 3. Create the WhatsApp preview

Create a deterministic 1200 × 630 JPEG from the exact supplied hero. This is a crop and resize only; it does not alter the source with generative editing.

```bash
python3 tools/create_og_preview.py \
  --hero /path/to/hero.png \
  --out /home/ubuntu/newsletter_DDMMMYYYY/preview.jpg
```

Use `--focus-x` or `--focus-y` only when the subject needs reframing. Review the final crop visually.

The finished issue must contain the following metadata, using its own date:

```html
<link rel="canonical" href="https://webes77.github.io/magnum-newsletter/issues/YYYY-MM-DD.html" />
<meta property="og:url" content="https://webes77.github.io/magnum-newsletter/issues/YYYY-MM-DD.html" />
<meta property="og:image" content="https://webes77.github.io/magnum-newsletter/assets/previews/YYYY-MM-DD.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:image" content="https://webes77.github.io/magnum-newsletter/assets/previews/YYYY-MM-DD.jpg" />
```

### 4. Validate the edition

| Check | Required result |
|---|---|
| Placeholders | No unresolved `{{...}}` markers |
| Editorial copy | No stale relative-date references |
| Images | Supplied assets appear in the required order |
| Mobile layout | Complete visual review passes |
| Social preview | JPEG is exactly 1200 × 630 and preserves the hero |
| Metadata | Canonical URL, `og:url`, `og:image`, dimensions, title, and description are correct |
| Archive | `issues.json` is valid and every linked issue file exists |

### 5. Publish the dated edition

Run the append-only publisher. Repeat `--content` once for each line shown on the archive card.

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

The publisher copies the finished files into their permanent dated paths, updates `issues.json`, checks every archive link, commits the issue, and pushes `main`. It never edits the archive homepage. Use `--replace` only when intentionally correcting an existing edition.

### 6. Verify the live result

Confirm that the archive, dated issue, and dated preview all return HTTP 200. Inspect the public issue HTML and verify that `og:url` points to the dated page and `og:image` points to the dated hero preview.

Share the **dated issue URL** on WhatsApp. Do not share the archive root when the current edition’s hero needs to appear. WhatsApp caches previews by URL, so a new dated URL also prevents an older edition’s image from being reused.
