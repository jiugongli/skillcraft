#!/usr/bin/env python3
"""Check whether image content is too close to the right or bottom edge."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops


def edge_has_content(image: Image.Image, edge: str, margin: int, threshold: int) -> bool:
    image = image.convert("RGB")
    width, height = image.size
    bg = image.getpixel((0, 0))
    if edge == "right":
        crop = image.crop((width - margin, 0, width, height))
    elif edge == "bottom":
        crop = image.crop((0, height - margin, width, height))
    else:
        raise ValueError(edge)
    diff = ImageChops.difference(crop, Image.new("RGB", crop.size, bg)).convert("L")
    return diff.point(lambda x: 255 if x > threshold else 0).getbbox() is not None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("images", nargs="+")
    parser.add_argument("--margin", type=int, default=100)
    parser.add_argument("--threshold", type=int, default=18)
    args = parser.parse_args()

    failed = False
    for raw in args.images:
        path = Path(raw)
        image = Image.open(path)
        right = edge_has_content(image, "right", args.margin, args.threshold)
        bottom = edge_has_content(image, "bottom", args.margin, args.threshold)
        status = "RISK" if right or bottom else "OK"
        print(f"{status}\t{path}\tright={right}\tbottom={bottom}")
        failed = failed or right or bottom
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
