#!/usr/bin/env python3
"""
Validate Codex compatibility for all skills in this repository.

Checks:
1) SKILL.md frontmatter: name + description and naming/length constraints.
2) agents/openai.yaml exists and has interface.display_name + short_description.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


ROOT_DIR = Path(__file__).resolve().parents[2]
MAX_SKILL_NAME_LENGTH = 64


def find_skill_dirs() -> list[Path]:
    return sorted(
        {
            path.parent
            for path in ROOT_DIR.glob("**/skills/**/SKILL.md")
            if ".git" not in path.parts and ".codex" not in path.parts
        }
    )


def validate_skill_md(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    content = skill_md.read_text()

    if not content.startswith("---"):
        return ["No YAML frontmatter found in SKILL.md"]

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return ["Invalid frontmatter format in SKILL.md"]

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return [f"Invalid YAML in SKILL.md frontmatter: {exc}"]

    if not isinstance(frontmatter, dict):
        return ["SKILL.md frontmatter must be a YAML dictionary"]

    name = frontmatter.get("name")
    description = frontmatter.get("description")

    if not isinstance(name, str) or not name.strip():
        errors.append("Missing or invalid frontmatter 'name'")
    else:
        stripped = name.strip()
        if not re.match(r"^[a-z0-9-]+$", stripped):
            errors.append("Skill name must be hyphen-case (lowercase letters, digits, hyphens)")
        if stripped.startswith("-") or stripped.endswith("-") or "--" in stripped:
            errors.append("Skill name cannot start/end with '-' or include consecutive '--'")
        if len(stripped) > MAX_SKILL_NAME_LENGTH:
            errors.append(f"Skill name exceeds {MAX_SKILL_NAME_LENGTH} chars")

    if not isinstance(description, str) or not description.strip():
        errors.append("Missing or invalid frontmatter 'description'")
    else:
        stripped = description.strip()
        if "<" in stripped or ">" in stripped:
            errors.append("Description cannot contain '<' or '>'")
        if len(stripped) > 1024:
            errors.append("Description exceeds 1024 chars")

    return errors


def validate_openai_yaml(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if not openai_yaml.exists():
        return ["Missing agents/openai.yaml"]

    try:
        data = yaml.safe_load(openai_yaml.read_text())
    except yaml.YAMLError as exc:
        return [f"Invalid YAML in agents/openai.yaml: {exc}"]

    if not isinstance(data, dict):
        return ["agents/openai.yaml must be a YAML dictionary"]

    interface = data.get("interface")
    if not isinstance(interface, dict):
        return ["agents/openai.yaml missing 'interface' map"]

    for key in ("display_name", "short_description"):
        value = interface.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"agents/openai.yaml missing interface.{key}")

    return errors


def main() -> None:
    skill_dirs = find_skill_dirs()
    if not skill_dirs:
        print("No skills found.")
        return

    failed = 0
    for skill_dir in skill_dirs:
        errors = []
        errors.extend(validate_skill_md(skill_dir))
        errors.extend(validate_openai_yaml(skill_dir))

        if errors:
            failed += 1
            rel = skill_dir.relative_to(ROOT_DIR)
            print(f"[FAIL] {rel}")
            for err in errors:
                print(f"  - {err}")

    if failed > 0:
        print(f"\nValidation failed: {failed}/{len(skill_dirs)} skills have issues.")
        sys.exit(1)

    print(f"Validation passed: {len(skill_dirs)} skills are Codex-compatible.")


if __name__ == "__main__":
    main()
