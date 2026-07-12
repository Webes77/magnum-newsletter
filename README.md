# Magnum AI — This Week in AI

The **Magnum AI** weekly newsletter is hosted on GitHub Pages:
**https://webes77.github.io/magnum-newsletter/**

- **`index.html`** — the current client-facing newsletter at the stable root URL.
- **`archive.html`** — the permanent issue library at `/archive.html`.
- **`issues.json`** — the manifest of every edition: date, title, summary, contents, and dated link.
- **`issues/`** — one permanent self-contained page per edition (`issues/YYYY-MM-DD.html`).
- **`assets/previews/`** — one 1200 × 630 hero-based WhatsApp preview per edition (`YYYY-MM-DD.jpg`).
- **`tools/`** — the deterministic build, preview, and publishing scripts used each week.

## Publishing a new edition

Every edition is published to the stable root and a permanent dated page in the same commit, paired with its hero preview and added to `issues.json`. The archive remains separate at `/archive.html`.

For a new WhatsApp broadcast, use the dated issue URL to avoid an older cached preview. The root must continue serving the current newsletter for clients who have already received or bookmarked that link.

The complete workflow and commands are in **[ADDING-AN-ISSUE.md](ADDING-AN-ISSUE.md)**.
