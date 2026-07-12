#!/usr/bin/env python3
"""Publish one Magnum AI newsletter to the live root and permanent archive.

The finished issue is copied to issues/YYYY-MM-DD.html and index.html. The root
copy points its canonical and og:url metadata at the stable client-facing URL;
the dated copy remains permanent. The archive stays at archive.html.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path

from PIL import Image

BASE_URL = "https://webes77.github.io/magnum-newsletter"
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
STALE_RE = re.compile(r"\b(last week|this week|yesterday|earlier today|prior edition|previous issue)\b", re.I)


def run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def validate_date(value: str) -> str:
    date.fromisoformat(value)
    return value


def validate_html(html_path: Path, issue_url: str, preview_url: str) -> None:
    html = html_path.read_text(encoding="utf-8")
    errors: list[str] = []
    if PLACEHOLDER_RE.search(html):
        errors.append("unresolved {{PLACEHOLDER}} marker")
    visible_body = re.search(r"<body\b[^>]*>(.*?)</body>", html, re.I | re.S)
    audit_text = visible_body.group(1) if visible_body else html
    audit_text = re.sub(r'<div\b[^>]*class="[^"]*\bprompt-box\b[^"]*"[^>]*>.*?</div>', " ", audit_text, flags=re.I | re.S)
    audit_text = re.sub(r"<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>", " ", audit_text, flags=re.I | re.S)
    audit_text = re.sub(r"<[^>]+>", " ", audit_text)
    audit_text = audit_text.replace("This Week in AI", "")
    if STALE_RE.search(audit_text):
        errors.append("stale relative-time reference in body copy")
    if issue_url not in html:
        errors.append(f"missing canonical issue URL: {issue_url}")
    if preview_url not in html:
        errors.append(f"missing issue preview URL: {preview_url}")
    if 'property="og:image:width" content="1200"' not in html:
        errors.append("missing og:image width 1200")
    if 'property="og:image:height" content="630"' not in html:
        errors.append("missing og:image height 630")
    if errors:
        raise ValueError("HTML validation failed: " + "; ".join(errors))


def validate_preview(preview_path: Path) -> None:
    with Image.open(preview_path) as image:
        if image.size != (1200, 630):
            raise ValueError(f"Preview must be 1200x630; got {image.size}")
        if image.format != "JPEG":
            raise ValueError(f"Preview must be JPEG; got {image.format}")


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("issues"), list):
        raise ValueError("issues.json must contain an issues array")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish a dated Magnum AI newsletter issue")
    parser.add_argument("--html", required=True, type=Path, help="Finished self-contained issue HTML")
    parser.add_argument("--preview", required=True, type=Path, help="1200x630 JPEG social preview")
    parser.add_argument("--date", required=True, type=validate_date, help="Publish date in YYYY-MM-DD")
    parser.add_argument("--display-date", required=True, help="Display date, e.g. 11 July 2026")
    parser.add_argument("--title", required=True, help="Issue headline")
    parser.add_argument("--dek", required=True, help="Archive summary and social description")
    parser.add_argument("--content", action="append", default=[], help="Archive contents line; repeat per section")
    parser.add_argument("--repo", type=Path, default=Path("/home/ubuntu/magnum-newsletter"))
    parser.add_argument("--replace", action="store_true", help="Explicitly replace an existing entry for this date")
    parser.add_argument("--push", action="store_true", help="Commit and push the issue after validation")
    args = parser.parse_args()

    repo = args.repo.resolve()
    html_source = args.html.resolve()
    preview_source = args.preview.resolve()
    manifest_path = repo / "issues.json"
    if not (repo / ".git").is_dir():
        raise FileNotFoundError(f"Not a Git repository: {repo}")
    if not html_source.is_file() or not preview_source.is_file():
        raise FileNotFoundError("HTML or preview input does not exist")
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Missing manifest: {manifest_path}")

    issue_rel = Path("issues") / f"{args.date}.html"
    preview_rel = Path("assets") / "previews" / f"{args.date}.jpg"
    issue_url = f"{BASE_URL}/{issue_rel.as_posix()}"
    preview_url = f"{BASE_URL}/{preview_rel.as_posix()}"

    validate_html(html_source, issue_url, preview_url)
    validate_preview(preview_source)

    manifest = load_manifest(manifest_path)
    existing = [item for item in manifest["issues"] if item.get("date") == args.date]
    if existing and not args.replace:
        raise ValueError(f"Issue {args.date} already exists; use --replace to update it explicitly")

    entry = {
        "date": args.date,
        "displayDate": args.display_date,
        "title": args.title,
        "dek": args.dek,
        "file": issue_rel.as_posix(),
        "contents": args.content,
    }
    manifest["issues"] = [item for item in manifest["issues"] if item.get("date") != args.date]
    manifest["issues"].append(entry)
    manifest["issues"].sort(key=lambda item: item["date"], reverse=True)

    issue_dest = repo / issue_rel
    preview_dest = repo / preview_rel
    root_dest = repo / "index.html"
    archive_dest = repo / "archive.html"
    if not archive_dest.is_file():
        raise FileNotFoundError(f"Missing archive homepage: {archive_dest}")

    issue_dest.parent.mkdir(parents=True, exist_ok=True)
    preview_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(html_source, issue_dest)
    shutil.copy2(preview_source, preview_dest)

    root_url = f"{BASE_URL}/"
    root_html = html_source.read_text(encoding="utf-8").replace(issue_url, root_url)
    root_dest.write_text(root_html, encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Parse the file we just wrote to guarantee valid JSON and verify every manifest path.
    saved = load_manifest(manifest_path)
    for item in saved["issues"]:
        linked = repo / item["file"]
        if not linked.is_file():
            raise FileNotFoundError(f"Manifest points to missing issue: {linked}")

    if args.push:
        run(["git", "add", issue_rel.as_posix(), preview_rel.as_posix(), "issues.json", "index.html"], repo)
        staged = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], cwd=repo, check=False
        ).returncode
        if staged == 0:
            print("No publication changes to commit.")
        else:
            run(["git", "commit", "-m", f"Add {args.display_date} edition: {args.title}"], repo)
            run(["git", "push", "origin", "main"], repo)

    print(f"Current: {BASE_URL}/")
    print(f"Issue:   {issue_url}")
    print(f"Preview: {preview_url}")
    print(f"Archive: {BASE_URL}/archive.html")


if __name__ == "__main__":
    main()
