# edition.json

One file describes one edition of This Week in AI. `tools/build_edition.py`
turns it into the dated page. `tools/example-edition.json` is the 23 August
2026 edition in this form and is the reference for tone and length.

## Top level

| Key | Type | Rule |
|---|---|---|
| `date` | string | Publish date, `YYYY-MM-DD`. Names the page, the preview and the asset folder. |
| `display_date` | string | The same date as printed, `13 September 2026`. |
| `title` | string | The edition headline. Appears in the page title, the archive and the members area card. Under ten words. |
| `dek` | string | One sentence for the archive card and the link preview. Under 30 words. |
| `hero_alt` | string | Alt text for the hero image. |
| `opener` | list of strings | Two to five short paragraphs. Italic on the page. Ends by pointing at the lead story. |
| `index` | list of `{label, line}` | One entry per section present, in section order. `line` is under 16 words, lower-case start. |
| `sections` | list of section objects | In the fixed order below. |
| `signoff` | list of strings | Two to four short paragraphs. The last one is a plain farewell. |

## Sections

Fixed order. The Newsline, Tool of the Week, Prompt of the Week and The
Magnum are required. Looking Sideways and The Win are optional and are
dropped from the page and the index when absent.

Every section has `label`, `headline` and `paragraphs` (a list of strings,
one sentence or two per paragraph, the way the reference edition reads).

| Label | Extra keys | What it is |
|---|---|---|
| `The Newsline` | none | The one story that changes what a small business owner does. Rendered as the page's h1. |
| `Looking Sideways` | none | Something from outside the AI news that shows where the tools are going. |
| `The Win` | none | A real result from a Magnum AI client, anonymised. Only written from material James supplied. Never invented. |
| `Tool of the Week` | `link: {url, text}` | One tool, what problem it solves, the price as quoted. `text` is `Name: url`. |
| `Prompt of the Week` | `prompt` (string, line breaks kept), `use` (list of strings, one instruction each) | A prompt a client can paste. Written for a named example business so the reader sees it filled in. |
| `The Magnum` | `prompt` (string), `image_alt` (string), `take` (string) | The image prompt that made the Magnum image, and one or two lines on what to take from it. |

## Copy rules the checker enforces

`build_edition.py` fails the check, and the publisher refuses the page, on
any of these.

- No em dash anywhere. A comma, a full stop or a middot instead.
- No relative time in body copy: "this week", "last week", "yesterday",
  "earlier today", "previous issue", "prior edition". Say the date or say
  "this edition". Inside a prompt box the rule does not apply.
- Never the word "solid".
- Sections in the fixed order, the four required ones present.

## Rules the checker cannot enforce

- Australian English. Plain sentences. Short paragraphs. Talks to one
  business owner, not to a list.
- No hype, no newsletter cliches, no exclamation marks.
- Figures, prices and names exactly as the source gave them. If unsure,
  leave it out.
- Nothing a reader would need to have read an earlier edition to follow.
