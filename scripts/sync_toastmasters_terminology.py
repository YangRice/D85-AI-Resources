#!/usr/bin/env python3
"""Synchronize the canonical Toastmasters glossary into skill packages."""

import argparse
import sys
from pathlib import Path


CANONICAL = Path("references/toastmasters-terminology.md")
MIRRORS: tuple[Path, ...] = (
    Path("skills/poster-image-translation-redesign/references/toastmasters-terminology.md"),
    Path("skills/powerpoint-translation-redesign/references/toastmasters-terminology.md"),
    Path("skills/egg-toastmasters-speech-mentor/references/d85-toastmasters-terminology.md"),
    Path("skills/translate-pdf/references/toastmasters-terminology.md"),
    Path("skills/prepare-successful-club-presentation/references/toastmasters-terminology.md"),
    Path("skills/toastmasters-speech-coaching-team/references/toastmasters-terminology.md"),
)


def render_mirror(canonical_text: str) -> str:
    return (
        f"<!-- Generated from {CANONICAL.as_posix()}. Do not edit this mirror manually. -->\n\n"
        + canonical_text
    )


def _mirror_destination(root: Path, relative: Path) -> Path:
    parts = relative.parts
    if (
        relative.is_absolute()
        or ".." in parts
        or len(parts) < 4
        or parts[0] != "skills"
        or parts[2] != "references"
    ):
        raise ValueError(f"Invalid mirror destination: {relative.as_posix()}")

    target = root
    for part in parts:
        target = target / part
        if target.is_symlink():
            raise ValueError(f"Symlink destination: {relative.as_posix()}")
    return target


def sync(root: Path, check: bool) -> list[str]:
    """Repair mirrors, or return their repository-relative paths when out of sync."""
    destinations = [(relative, _mirror_destination(root, relative)) for relative in MIRRORS]
    try:
        canonical_text = (root / CANONICAL).read_bytes().decode("utf-8")
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Missing canonical glossary: {CANONICAL.as_posix()}") from error
    expected = render_mirror(canonical_text).encode("utf-8")

    mismatches = []
    for relative, target in destinations:
        if target.is_file() and target.read_bytes() == expected:
            continue
        if check:
            mismatches.append(relative.as_posix())
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(expected)
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report missing or drifted mirrors without writing")
    args = parser.parse_args()
    try:
        mismatches = sync(Path(__file__).resolve().parents[1], check=args.check)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    if mismatches:
        print("Out-of-sync terminology mirrors:", file=sys.stderr)
        for path in mismatches:
            print(f"  {path}", file=sys.stderr)
        print("Run: python3 scripts/sync_toastmasters_terminology.py", file=sys.stderr)
        return 1
    print("Toastmasters terminology mirrors match the canonical glossary" if args.check else
          "Toastmasters terminology mirrors synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
