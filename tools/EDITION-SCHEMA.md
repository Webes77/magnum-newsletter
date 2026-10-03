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
| `whatsapp` | string | The message James pastes into the WhatsApp broadcast above the link. Under 60 words, his voice, no link in it, ends with "Four minutes." Not rendered on the page; the publish run emails it with the link. |

## Sections

Fixed order. The Newsline, Tool of the Week, Prompt of the Week and The
Magnum are required. Looking Sideways and The Win are optional and are
dropped from the page and the index when absent.

Every section has `label`, `headline` and `paragraphs` (a list of strings,
one sentence or two per paragraph, the way the reference edition reads).

| Label | Extra keys | What it is |
|---|---|---|
| `The Newsline` | `source` (required) | The one story that changes what a small business owner does. Rendered as the page's h1. |
| `Looking Sideways` | `source` (required) | Something from outside the AI news that shows where the tools are going. |
| `The Win` | none | A real result from a Magnum AI client, anonymised. Only written from material James supplied. Never invented. |
| `Tool of the Week` | `link: {url, text}` | One tool, what problem it solves, the price as quoted. `text` is `Name: url`. |
| `Prompt of the Week` | `prompt` (string, line breaks kept), `use` (list of strings, one instruction each) | A prompt any small business owner can paste, whatever their trade. Generic, never written for one named or example business; the reader's own details go in short [square bracket] fill-ins, three or four at most. |
| `The Magnum` | `prompt` (string), `image_alt` (string), `take` (string), optional `video_prompt` (string) | The image prompt that made the Magnum image, and one or two lines on what to take from it. When the Magnum is a video made in two steps (a still, then a video model animating it), `video_prompt` carries the motion prompt verbatim; the page then labels the two boxes "The image prompt" and "The video prompt". When the Magnum is a video, the builder takes a frame from it as the still shown before it plays (`video_poster`, set automatically; it needs ffmpeg, so `pip install imageio-ffmpeg` first). `--magnum-poster` overrides the frame with a chosen still. The check fails if the video has no poster. |

### Sources

Any section may carry an optional `source` object. It renders as a coral
mono link at the end of the section and, when `image` is given, as a
full-width image at the top of the section body with a small
"Image: publisher.com" credit under it. If the image fails to load it is
hidden, so a broken third-party link never shows a broken picture.

```json
"source": {
  "url": "https://openai.com/index/...",
  "text": "Read the original: OpenAI's announcement",
  "image": "https://... (optional, the article's own main image)",
  "image_alt": "... (required when image is given)"
}
```

| Key | Rule |
|---|---|
| `url` | Required. The original article. Starts with `https://`. |
| `text` | Required, not empty. `Read the original: <publisher>`, optionally with what it is. |
| `image` | Optional. The article's own main image, hotlinked, `https://`. Leave it out rather than guess. |
| `image_alt` | Required when `image` is given. Describes the picture. |

The Newsline and Looking Sideways must carry a source (Looking Sideways only
when it is present). Tool of the Week keeps its existing `link` and carries
no `source`. The Win, Prompt of the Week and The Magnum carry none.

## Copy rules the checker enforces

`build_edition.py` fails the check, and the publisher refuses the page, on
any of these.

- No em dash anywhere. A comma, a full stop or a middot instead.
- No relative time in body copy: "this week", "last week", "yesterday",
  "earlier today", "previous issue", "prior edition". Say the date or say
  "this edition". Inside a prompt box the rule does not apply.
- Never the word "solid".
- Sections in the fixed order, the four required ones present.
- The Newsline carries a `source`, and so does Looking Sideways when present.
  Every `source` has an `https://` url and non-empty text; an `image` needs
  `image_alt`. The Win, Prompt of the Week and The Magnum carry none.

## Rules the checker cannot enforce

- Australian English. Plain sentences. Short paragraphs. Talks to one
  business owner, not to a list.
- No hype, no newsletter cliches, no exclamation marks.
- Figures, prices and names exactly as the source gave them. If unsure,
  leave it out.
- Nothing a reader would need to have read an earlier edition to follow.
- Source names may appear only in the source line, never in body copy.
