#!/usr/bin/env python3
"""Extract PPTX paragraph text and flag likely source-language remnants."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
SLIDE_RE = re.compile(r"ppt/slides/slide(\d+)\.xml$")
LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z'-]{2,}")


def paragraphs(xml_bytes: bytes) -> list[str]:
    root = ET.fromstring(xml_bytes)
    values = []
    for paragraph in root.findall(".//a:p", NS):
        text = "".join(node.text or "" for node in paragraph.findall(".//a:t", NS))
        text = " ".join(text.split())
        if text:
            values.append(text)
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--language", choices=["en"], help="Flag likely remnants")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    if not args.pptx.is_file():
        parser.error(f"file not found: {args.pptx}")

    slides = []
    with zipfile.ZipFile(args.pptx) as archive:
        names = sorted(
            (name for name in archive.namelist() if SLIDE_RE.match(name)),
            key=lambda name: int(SLIDE_RE.match(name).group(1)),
        )
        for name in names:
            number = int(SLIDE_RE.match(name).group(1))
            items = paragraphs(archive.read(name))
            flagged = [text for text in items if args.language == "en" and LATIN_WORD.search(text)]
            slides.append({"slide": number, "paragraphs": items, "flagged": flagged})

    counts = Counter(text for slide in slides for text in slide["paragraphs"])
    result = {
        "file": str(args.pptx.resolve()),
        "slide_count": len(slides),
        "slides": slides,
        "repeated_paragraphs": [
            {"text": text, "count": count}
            for text, count in counts.most_common()
            if count > 1
        ],
    }
    if args.json:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        print(f"Slides: {result['slide_count']}")
        for slide in slides:
            for text in slide["flagged"]:
                print(f"slide {slide['slide']}: {text}")
        print(f"Repeated paragraphs: {len(result['repeated_paragraphs'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
