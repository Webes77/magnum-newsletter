# Magnum AI — This Week in AI

The public archive for the **Magnum AI** weekly newsletter, hosted on GitHub Pages:
**https://webes77.github.io/magnum-newsletter/**

- **`index.html`** — the archive homepage. Lists every edition, newest first. It builds the
  list automatically from `issues.json`, so it rarely needs editing.
- **`issues.json`** — the manifest of every edition (date, title, summary, contents, link).
- **`issues/`** — one self-contained HTML page per edition (`issues/YYYY-MM-DD.html`).
- **`thumbnail.png`** — shared social-preview image.

## Publishing a new edition

The whole process is: add the issue's HTML page under `issues/`, add one entry to
`issues.json`, and push to `main`. GitHub Pages republishes automatically.

Full step-by-step instructions (written for the agent that builds the newsletter) live in
**[ADDING-AN-ISSUE.md](ADDING-AN-ISSUE.md)**.
