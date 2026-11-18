#!/usr/bin/env python3
"""
build_email.py

Turns one edition.json into the subscriber email for This Week in AI, so the
Sunday run never hand-writes email HTML. Added 19 November 2026, when the
newsletter moved from WhatsApp to email (MailerLite).

    python3 tools/build_email.py --edition build/YYYY-MM-DD/edition.json \
        --out build/YYYY-MM-DD/email.html

The email is a teaser: the date, the opener, every headline as a numbered
contents list, one button to the full edition, and the sign-off. It matches
the Field Note email in magnum-guides (templates/field-note-email.html), so
both emails look like one newsletter. {$unsubscribe} is left for MailerLite.
"""

import argparse
import html
import json
import sys
from pathlib import Path

BASE_URL = "https://webes77.github.io/magnum-newsletter"
BANNER_URL = f"{BASE_URL}/assets/standing/banner.jpg"
LOGO_URL = "https://members.magnumai.com.au/assets/logos/magnum-mark-email.png"
WIDTH = 760

SANS = "'IBM Plex Sans',Arial,Helvetica,sans-serif"
DISPLAY = "'Oswald','Arial Narrow',Arial,sans-serif"
LABEL = (f"margin:0 0 8px;font-family:{SANS};font-size:13px;font-weight:600;"
         "letter-spacing:1px;text-transform:uppercase;color:#C63A2A;")
BODY = f"margin:0 0 16px;font-family:{SANS};font-size:17px;line-height:1.55;color:#2B2823;"


def e(text: str) -> str:
    return html.escape(text, quote=True)


def build(data: dict) -> str:
    d = data["date"]
    url = f"{BASE_URL}/issues/{d}.html"
    opener = "\n".join(f'      <p style="{BODY}">{e(p)}</p>' for p in data["opener"])
    rows = []
    for n, s in enumerate(data["sections"], 1):
        rows.append(f"""        <tr>
          <td width="44" valign="top" style="width:44px;padding:0 0 12px;font-family:{DISPLAY};font-size:22px;line-height:1.2;font-weight:700;color:#C63A2A;">{n:02d}</td>
          <td valign="top" style="padding:2px 0 12px;font-family:{SANS};font-size:17px;line-height:1.45;">
            <a href="{url}#s{n:02d}" style="color:#1E1B17;text-decoration:none;font-weight:600;">{e(s["headline"])}</a>
            <div style="font-family:{SANS};font-size:13px;line-height:1.4;color:#63615C;padding-top:2px;">{e(s["label"])}</div>
          </td>
        </tr>""")
    contents = "\n".join(rows)
    signoff = "\n".join(f'      <p style="{BODY}">{e(p)}</p>' for p in data["signoff"])
    greeting = e(data.get("greeting", "Happy Sunday."))
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<title>This Week in AI: {e(data["title"])}</title>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@600;700&family=IBM+Plex+Sans:wght@400;600&display=swap" rel="stylesheet">
</head>
<body style="margin:0;padding:0;background:#FBFBF9;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{e(data["dek"])}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#FBFBF9;">
<tr><td align="center" style="padding:20px 10px 32px;">
  <table role="presentation" width="{WIDTH}" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:{WIDTH}px;background:#FFFFFF;border:2px solid #1E1B17;">

    <tr><td style="padding:18px 28px 16px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
        <td width="60" valign="middle" style="width:60px;"><img src="{LOGO_URL}" width="56" height="56" alt="Magnum AI" style="display:block;border:0;width:56px;height:56px;"></td>
        <td valign="middle" style="padding-left:12px;">
          <div style="font-family:{DISPLAY};font-size:24px;line-height:1.1;font-weight:700;text-transform:uppercase;color:#1E1B17;">This Week in AI</div>
          <div style="font-family:{SANS};font-size:14px;line-height:1.4;font-weight:600;color:#C63A2A;padding-top:3px;">{e(data["display_date"])} &middot; from James at Magnum AI</div>
        </td>
      </tr></table>
    </td></tr>

    <tr><td style="background:#1F2A37;padding:14px 28px;font-family:{SANS};font-size:16px;line-height:1.5;color:#F4F1EA;">
      The week's AI news that matters to a small business, in plain words.
    </td></tr>

    <tr><td style="padding:0;border-bottom:2px solid #1E1B17;">
      <a href="{url}" style="display:block;"><img src="{BANNER_URL}" width="{WIDTH - 4}" alt="This Week in AI" style="display:block;border:0;width:100%;max-width:{WIDTH - 4}px;height:auto;"></a>
    </td></tr>

    <tr><td style="padding:26px 28px 6px;">
      <h1 style="margin:0 0 18px;font-family:{DISPLAY};font-size:32px;line-height:1.1;font-weight:700;text-transform:uppercase;color:#1E1B17;">{e(data["title"])}</h1>
      <p style="{BODY}font-weight:600;">{greeting}</p>
{opener}
      <p style="{LABEL}padding-top:6px;">In this edition</p>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
{contents}
      </table>
    </td></tr>

    <tr><td align="left" style="padding:8px 28px 28px;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
        <td style="background:#C63A2A;border:2px solid #1E1B17;">
          <a href="{url}" style="display:inline-block;padding:15px 26px;font-family:{SANS};font-size:16px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#FFFFFF;text-decoration:none;">Read this week's edition</a>
        </td>
      </tr></table>
      <p style="margin:12px 0 0;font-family:{SANS};font-size:14px;line-height:1.5;color:#63615C;">About four minutes to read. Every headline above opens its story.</p>
    </td></tr>

    <tr><td style="padding:22px 28px 24px;border-top:2px solid #1E1B17;background:#FBFBF9;">
{signoff}
      <p style="margin:0;font-family:{SANS};font-size:17px;line-height:1.5;color:#2B2823;">Any questions, just reply to this email. It comes straight to me.</p>
      <p style="margin:10px 0 0;font-family:{SANS};font-size:17px;line-height:1.5;font-weight:600;color:#1E1B17;">James</p>
    </td></tr>

  </table>

  <table role="presentation" width="{WIDTH}" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:{WIDTH}px;">
    <tr><td style="padding:18px 6px 0;font-family:{SANS};font-size:13px;line-height:1.6;color:#63615C;">
      You are getting this because you subscribed to the Magnum AI newsletter.<br>
      Magnum AI, Suite 4, 35 Cedric Street, Stirling WA 6021, Australia<br>
      <a href="{{$unsubscribe}}" style="color:#63615C;text-decoration:underline;">Unsubscribe</a>
    </td></tr>
  </table>
</td></tr>
</table>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--edition", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    data = json.loads(a.edition.read_text(encoding="utf-8"))
    for k in ("date", "display_date", "title", "dek", "opener", "sections", "signoff"):
        if k not in data:
            print(f"edition.json has no {k}", file=sys.stderr)
            return 1
    out = build(data)
    if "—" in out:
        print("an em dash got into the email; fix edition.json", file=sys.stderr)
        return 1
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(out, encoding="utf-8")
    print(f"Wrote {a.out} ({len(out)} characters)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
