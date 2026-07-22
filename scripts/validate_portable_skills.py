#!/usr/bin/env python3
"""Validate the D85 portable Toastmasters skill catalog using only stdlib."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog" / "skills.json"
INTEGRATIONS_PATH = ROOT / "catalog" / "integrations.json"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot load {path.relative_to(ROOT)}: {exc}") from exc


def parse_frontmatter(skill_md: Path) -> tuple[str, str, str]:
    text = skill_md.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{skill_md.relative_to(ROOT)} has invalid frontmatter")
    fields = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields.get("name", ""), fields.get("description", ""), text


def detect_cycles(graph: dict[str, list[str]]) -> list[str]:
    visiting: set[str] = set()
    visited: set[str] = set()
    errors: list[str] = []

    def visit(node: str, path: list[str]) -> None:
        if node in visiting:
            start = path.index(node)
            errors.append("Dependency cycle: " + " -> ".join(path[start:] + [node]))
            return
        if node in visited:
            return
        visiting.add(node)
        for child in graph.get(node, []):
            visit(child, path + [child])
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node, [node])
    return errors


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        catalog = load_json(CATALOG_PATH)
        integrations = load_json(INTEGRATIONS_PATH)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    skills = catalog.get("skills", [])
    actions = integrations.get("actions", {})
    by_id: dict[str, dict] = {}

    for item in skills:
        skill_id = item.get("id", "")
        if not NAME_RE.fullmatch(skill_id):
            errors.append(f"Invalid skill id: {skill_id!r}")
            continue
        if skill_id in by_id:
            errors.append(f"Duplicate skill id: {skill_id}")
        by_id[skill_id] = item

        if item.get("type") not in {"atomic", "journey"}:
            errors.append(f"{skill_id}: type must be atomic or journey")
        if not item.get("resource_page"):
            errors.append(f"{skill_id}: missing future Resource Center page slug")

        skill_dir = ROOT / "skills" / skill_id
        skill_md = skill_dir / "SKILL.md"
        agent_yaml = skill_dir / "agents" / "openai.yaml"
        if not skill_md.exists():
            errors.append(f"{skill_id}: SKILL.md is missing")
            continue
        if not agent_yaml.exists():
            errors.append(f"{skill_id}: agents/openai.yaml is missing")
        try:
            name, description, text = parse_frontmatter(skill_md)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            continue
        if name != skill_id:
            errors.append(f"{skill_id}: frontmatter name is {name!r}")
        if not description or "TODO" in description or "TODO" in text:
            errors.append(f"{skill_id}: incomplete description or TODO remains")
        if len(text.splitlines()) > 500:
            errors.append(f"{skill_id}: SKILL.md exceeds 500 lines")
        if agent_yaml.exists():
            agent_text = agent_yaml.read_text(encoding="utf-8")
            if f"${skill_id}" not in agent_text:
                errors.append(f"{skill_id}: default prompt does not mention ${skill_id}")

    graph: dict[str, list[str]] = {}
    for skill_id, item in by_id.items():
        dependencies = item.get("requires", []) + item.get("recommends", [])
        graph[skill_id] = dependencies
        for dep in dependencies:
            if dep not in by_id:
                label = "required" if dep in item.get("requires", []) else "recommended"
                errors.append(f"{skill_id}: missing {label} dependency {dep}")
        if item.get("type") == "atomic" and dependencies:
            warnings.append(f"{skill_id}: atomic skill declares composition dependencies")
        for action in item.get("actions", []):
            if action not in actions:
                errors.append(f"{skill_id}: unknown action {action}")

    errors.extend(detect_cycles(graph))

    for action_id, action in actions.items():
        url = action.get("url", "")
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"Action {action_id}: invalid HTTPS URL {url!r}")
        if action.get("required") is not False:
            errors.append(f"Action {action_id}: external actions must remain optional")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"Validation failed with {len(errors)} error(s).")
        return 1
    print(
        f"Validated {len(by_id)} skills "
        f"({sum(s['type'] == 'journey' for s in by_id.values())} journey, "
        f"{sum(s['type'] == 'atomic' for s in by_id.values())} atomic) "
        f"and {len(actions)} optional actions."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
