#!/bin/bash
# Safe wrapper for publishing a dated Magnum AI newsletter issue.
# Never overwrites index.html.
#
# Usage:
#   bash push_to_github.sh \
#     --html /path/to/issue.html \
#     --preview /path/to/preview.jpg \
#     --date 2026-07-11 \
#     --display-date "11 July 2026" \
#     --title "It came back finished" \
#     --dek "Issue summary" \
#     --content "The Newsline — ..." \
#     --content "The Magnum — ..." \
#     --push

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/publish_weekly_issue.py" "$@"
