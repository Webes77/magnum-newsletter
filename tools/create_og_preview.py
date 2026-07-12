#!/usr/bin/env python3
"""Create a WhatsApp/Open Graph preview from a supplied newsletter hero.

The operation is deterministic: EXIF orientation correction, RGB conversion,
cover crop, resize to 1200x630, and JPEG export. No generative editing occurs.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps

SIZE = (1200, 630)


def build_preview(source: Path, output: Path, focus_x: float, focus_y: float, quality: int) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"Hero image not found: {source}")
    if not 0 <= focus_x <= 1 or not 0 <= focus_y <= 1:
        raise ValueError("focus-x and focus-y must be between 0 and 1")

    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        preview = ImageOps.fit(
            image,
            SIZE,
            method=Image.Resampling.LANCZOS,
            centering=(focus_x, focus_y),
        )
        preview.save(output, "JPEG", quality=quality, optimize=True, progressive=True)

    with Image.open(output) as check:
        if check.size != SIZE:
            raise RuntimeError(f"Preview has incorrect dimensions: {check.size}")

    print(f"Created {output} ({output.stat().st_size / 1024:.0f} KB, 1200x630)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a 1200x630 newsletter social preview")
    parser.add_argument("--hero", required=True, type=Path, help="Supplied hero image")
    parser.add_argument("--out", required=True, type=Path, help="Output JPEG path")
    parser.add_argument("--focus-x", type=float, default=0.5, help="Horizontal focal point, 0 to 1")
    parser.add_argument("--focus-y", type=float, default=0.45, help="Vertical focal point, 0 to 1")
    parser.add_argument("--quality", type=int, default=88, help="JPEG quality, 1 to 95")
    args = parser.parse_args()
    build_preview(args.hero, args.out, args.focus_x, args.focus_y, args.quality)


if __name__ == "__main__":
    main()
