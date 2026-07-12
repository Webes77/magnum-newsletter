# Magnum AI — This Week in AI

The public archive for the **Magnum AI** weekly newsletter, hosted on GitHub Pages:
**https://webes77.github.io/magnum-newsletter/**

- **`index.html`** — the permanent archive homepage. It lists every edition from `issues.json` and is never replaced by a weekly issue.
- **`issues.json`** — the manifest of every edition: date, title, summary, contents, and dated link.
- **`issues/`** — one self-contained HTML page per edition (`issues/YYYY-MM-DD.html`).
- **`assets/previews/`** — one 1200 × 630 hero-based WhatsApp preview per edition (`YYYY-MM-DD.jpg`).
- **`tools/`** — the deterministic build, preview, and append-only publishing scripts used each week.
- **`thumbnail.png`** — the archive homepage’s shared social-preview image.

## Publishing a new edition

Every edition is built as a dated self-contained page, paired with a dated hero preview, added to `issues.json`, and pushed to `main`. GitHub Pages republishes the archive automatically. The dated issue URL—not the archive root—is the WhatsApp share link.

The complete tested workflow and commands are in **[ADDING-AN-ISSUE.md](ADDING-AN-ISSUE.md)**.
