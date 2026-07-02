#!/usr/bin/env python3
"""Merge ordered report pages into a vertical long image with safe margins."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("images", nargs="+", help="Ordered input images")
    parser.add_argument("--out", required=True)
    parser.add_argument("--canvas-width", type=int, default=1800)
    parser.add_argument("--inner-width", type=int, default=1480)
    parser.add_argument("--separator", type=int, default=34)
    parser.add_argument("--bg", default="246,244,238")
    parser.add_argument("--sep-color", default="226,223,214")
    args = parser.parse_args()

    bg = tuple(int(x) for x in args.bg.split(","))
    sep_color = tuple(int(x) for x in args.sep_color.split(","))
    side = (args.canvas_width - args.inner_width) // 2

    pages = []
    for raw in args.images:
        image = Image.open(raw).convert("RGB")
        new_height = round(image.height * args.inner_width / image.width)
        resized = image.resize((args.inner_width, new_height), Image.Resampling.LANCZOS)
        page = Image.new("RGB", (args.canvas_width, new_height), bg)
        page.paste(resized, (side, 0))
        pages.append(page)

    total_height = sum(page.height for page in pages) + args.separator * (len(pages) - 1)
    long_image = Image.new("RGB", (args.canvas_width, total_height), bg)
    draw = ImageDraw.Draw(long_image)
    y = 0
    for index, page in enumerate(pages):
        long_image.paste(page, (0, y))
        y += page.height
        if index < len(pages) - 1:
            draw.rectangle((0, y, args.canvas_width, y + args.separator), fill=sep_color)
            y += args.separator

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    long_image.save(args.out, quality=92)
    print(args.out)
    print(long_image.size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
