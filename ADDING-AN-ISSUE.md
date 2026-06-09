# Adding a new weekly issue (instructions for Manus)

This repository is the public archive for the **Magnum AI — _This Week in AI_** newsletter.
It is hosted on GitHub Pages at **https://webes77.github.io/magnum-newsletter/**.

The homepage builds its list of editions **automatically** from `issues.json`. That means
publishing a new edition is just: drop in one HTML file, add one entry to a list, and push.
**You never need to edit `index.html`.**

---

## Repository layout

| Path | What it is |
|------|------------|
| `index.html` | The archive homepage. Renders the issue list from `issues.json`. **Don't edit for new issues.** |
| `issues.json` | The list of every edition. **This is the only file you append to.** |
| `issues/` | One self-contained HTML page per edition (`issues/YYYY-MM-DD.html`). |
| `thumbnail.png` | Shared 1200×630 social-preview image. |
| `ADDING-AN-ISSUE.md` | This file. |

---

## Publish a new edition — 3 steps

### 1. Save the newsletter as an issue page

Save the finished newsletter HTML to:

```
issues/YYYY-MM-DD.html        e.g. issues/2026-06-13.html
```

using the **publish date**. Requirements for that file:

- Keep it **self-contained** — embed images as `data:` URIs or use absolute `https://` URLs.
  Do **not** use relative asset paths (they break once the file is in the `issues/` subfolder).
- In its `<head>`, set the canonical / Open Graph URL to the page's **own** address:

  ```html
  <meta property="og:url" content="https://webes77.github.io/magnum-newsletter/issues/2026-06-13.html" />
  ```

- `og:image` may stay `https://webes77.github.io/magnum-newsletter/thumbnail.png`,
  or point to your own 1200×630 image.

### 2. Add one entry to `issues.json`

Add an object to the `"issues"` array. **Order doesn't matter** — the homepage sorts by
`date` (newest first) and automatically gives the newest edition the **"Latest"** badge and
updates the "_N issues and counting_" count. A new entry looks like:

```json
{
  "date": "2026-06-13",
  "displayDate": "13 June 2026",
  "title": "Your edition headline",
  "dek": "One or two sentences that appear under the headline on the homepage card.",
  "file": "issues/2026-06-13.html",
  "contents": [
    "Looking Sideways — short description",
    "Real Wins — short description",
    "Tool of the Week — short description",
    "Prompt of the Week — short description",
    "The Magnum — short description"
  ]
}
```

**Field reference**

| Field | Required | Notes |
|-------|----------|-------|
| `date` | yes | ISO `YYYY-MM-DD`. Used for sorting only. |
| `displayDate` | yes | How the date reads on the card, e.g. `"13 June 2026"`. |
| `title` | yes | The edition's headline. |
| `dek` | yes | Short summary sentence(s) shown under the headline. |
| `file` | yes | Path to the issue page: `"issues/YYYY-MM-DD.html"`. Must match the real filename exactly. |
| `contents` | recommended | Array of section lines. Use `—` between the section name and its description. |

### 3. Commit and push to `main`

```bash
git add issues.json issues/YYYY-MM-DD.html
git commit -m "Add 13 June 2026 edition: Your edition headline"
git push origin main
```

GitHub Pages republishes from `main` automatically. The new edition appears on the homepage
within about a minute. **That's it — no other steps.**

---

## Rules & gotchas

- **Only ever _add_ to `issues.json`** — never remove or rename past editions; their URLs are public.
- `issues.json` **must stay valid JSON**: separate every entry with a comma, and **no trailing
  comma** after the last one.
- Use real Unicode punctuation in the JSON text (`’ ‘ “ ” —`), **not** HTML entities like
  `&rsquo;` — the homepage escapes and renders the text for you.
- **Don't touch `index.html`** for routine issues. It builds everything from `issues.json`.
- **Don't move or rename** existing `issues/*.html` files.

## Self-check before pushing

```bash
python3 -m json.tool issues.json    # must print with no error  → JSON is valid
```

Then confirm:

- the new `issues/YYYY-MM-DD.html` opens in a browser and looks right, and
- the `"file"` value in `issues.json` exactly matches the new filename.

If all three pass, push to `main`.
