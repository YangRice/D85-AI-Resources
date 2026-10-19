#!/usr/bin/env python3
"""Check all tracked D85 skill packages, using only Python's standard library.

This checks distributed files, not client discovery or workflow readiness.
For a clean export, supply a manifest captured with `git ls-files` at its source.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---(?:\n|$)", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^\s)]+)\)")
# Native contract outside the portable catalog: needed when a deck contains
# raster text. Check distribution availability, not whether a task needs it.
NATIVE_COMPANIONS = {
    "powerpoint-translation-redesign": ("poster-image-translation-redesign",),
    "poster-image-translation-redesign": (
        "toastmasters-poster-maker", "toastmasters-poster-reviewer", "edit-svg-canvas",
    ),
}


def tracked_files(root: Path, manifest: Path | None) -> set[str]:
    if manifest:
        names = manifest.read_text(encoding="utf-8").splitlines()
    else:
        top = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL, text=True,
        ).strip()
        if Path(top).resolve() != root:
            raise ValueError("--root must be the repository root; exports need --tracked-files")
        names = subprocess.check_output(
            ["git", "-C", str(root), "ls-files", "-z"], text=True,
        ).split("\0")
    files = {name for name in names if name}
    for name in files:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"Invalid tracked path: {name!r}")
    return files


def validate(root: Path, files: set[str]) -> tuple[list[str], list[str]]:
    packages = sorted(
        PurePosixPath(name).parts[1] for name in files
        if len(PurePosixPath(name).parts) == 3
        and name.startswith("skills/") and name.endswith("/SKILL.md")
    )
    errors = []
    if not packages:
        return packages, ["No tracked skills/*/SKILL.md packages found"]
    bundled = sorted(name for name in files if len(PurePosixPath(name).parts) >= 3
                     and name.startswith("skills/") and PurePosixPath(name).parts[1] in packages)
    for name in bundled:
        path = root / name
        if not path.is_file():
            errors.append(f"Missing bundled file: {name}")
            continue
        if path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        # Canonical SKILL.md is the native entry point. A translated companion
        # may be plain prose; if it declares frontmatter, validate its identity.
        if path.name == "SKILL.md" or (path.name == "SKILL.zh.md" and text.startswith("---\n")):
            match = FRONTMATTER_RE.match(text)
            fields = {}
            if not match:
                errors.append(f"{name}: invalid frontmatter")
            else:
                for line in match.group(1).splitlines():
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        if key in fields:
                            errors.append(f"{name}: duplicate frontmatter field {key}")
                        fields[key] = value.strip().strip("\"'")
                identity = fields.get("name", "")
                expected = PurePosixPath(name).parts[1]
                if not NAME_RE.fullmatch(identity) or identity != expected:
                    errors.append(f"{name}: frontmatter name {identity!r} must match {expected!r}")
                if not fields.get("description"):
                    errors.append(f"{name}: missing frontmatter description")
        for link in LINK_RE.findall(text):
            url = urlsplit(link.strip("<>"))
            if url.scheme or url.netloc or not url.path:
                continue
            target = (path.parent / unquote(url.path)).resolve()
            if not target.is_relative_to(root):
                errors.append(f"{name}: local link escapes collection: {link}")
                continue
            relative = target.relative_to(root).as_posix()
            if relative not in files or not target.is_file():
                errors.append(f"{name}: missing tracked local link target {relative}")

    companions = dict(NATIVE_COMPANIONS)
    catalog_path = root / "catalog/skills.json"
    if "catalog/skills.json" in files:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        for item in catalog["skills"]:
            companions[item["id"]] = tuple(item.get("requires", [])) + tuple(item.get("recommends", []))
    for skill, dependencies in companions.items():
        if skill in packages:
            for dependency in dependencies:
                if dependency not in packages:
                    errors.append(f"{skill}: missing collection companion {dependency} (required or conditional; see skill contract)")
    return packages, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository or clean export root")
    parser.add_argument("--tracked-files", type=Path, help="source git ls-files output (one path per line) for exports")
    args = parser.parse_args()
    try:
        packages, errors = validate(args.root.resolve(), tracked_files(args.root.resolve(), args.tracked_files))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: Cannot validate collection: {exc}")
        return 1
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"Package validation failed with {len(errors)} error(s).")
        return 1
    print(f"Validated {len(packages)} skill packages (local static checks only).")
    print("Packages: " + ", ".join(packages))
    print("Client discovery/loading, runtime tools and workflow readiness remain unverified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
