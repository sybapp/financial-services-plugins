#!/usr/bin/env python3
"""
Adapt this repository's skills for Codex-compatible usage.

What this script does:
1) Ensure every SKILL.md has YAML frontmatter with name + description.
2) Move inline "description: ..." lines into frontmatter when needed.
3) Create agents/openai.yaml for skills that do not have one.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml


ROOT_DIR = Path(__file__).resolve().parents[2]
MAX_SHORT_DESC = 64
MIN_SHORT_DESC = 25

ACRONYMS = {"API", "CLI", "DCF", "LBO", "MCP", "PE", "PPT", "QC"}


def find_skill_files() -> list[Path]:
    pattern = "**/skills/**/SKILL.md"
    files = [p for p in ROOT_DIR.glob(pattern) if ".git" not in p.parts and ".codex" not in p.parts]
    return sorted(files)


def parse_frontmatter(content: str) -> tuple[dict | None, str]:
    if not content.startswith("---\n"):
        return None, content
    match = re.match(r"^---\n(.*?)\n---\n?", content, re.DOTALL)
    if not match:
        return None, content

    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        data = None

    if not isinstance(data, dict):
        data = None
    body = content[match.end() :]
    return data, body


def pop_inline_description(body: str) -> tuple[str, str | None]:
    lines = body.splitlines()
    search_window = min(40, len(lines))

    for idx in range(search_window):
        match = re.match(r"^\s*description:\s*(.+?)\s*$", lines[idx])
        if not match:
            continue
        description = match.group(1).strip()
        del lines[idx]

        # Remove an extra empty spacer right after description to avoid double blank lines.
        if idx < len(lines) and lines[idx].strip() == "":
            if idx == 0 or lines[idx - 1].strip() == "":
                del lines[idx]

        new_body = "\n".join(lines)
        if body.endswith("\n"):
            new_body += "\n"
        return new_body, description

    return body, None


def format_display_name(skill_name: str) -> str:
    words = [w for w in skill_name.split("-") if w]
    formatted = []
    for word in words:
        upper = word.upper()
        if upper in ACRONYMS:
            formatted.append(upper)
        else:
            formatted.append(word.capitalize())
    return " ".join(formatted)


def make_default_description(skill_name: str) -> str:
    natural = skill_name.replace("-", " ")
    return (
        f"Guidance for {natural} workflows. Use when requests involve "
        f"{natural} analysis, execution, or deliverables."
    )


def clamp_short_description(raw: str, display_name: str) -> str:
    text = " ".join(raw.split())
    if len(text) > MAX_SHORT_DESC:
        sentence = re.split(r"(?<=[.!?])\s+", text)[0]
        if MIN_SHORT_DESC <= len(sentence) <= MAX_SHORT_DESC:
            return sentence
        text = text[: MAX_SHORT_DESC - 3].rstrip() + "..."

    if len(text) < MIN_SHORT_DESC:
        fallback = f"Help with {display_name} tasks and workflows"
        if len(fallback) > MAX_SHORT_DESC:
            fallback = fallback[:MAX_SHORT_DESC].rstrip()
        text = fallback

    return text


def yaml_quote(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def ensure_openai_yaml(skill_dir: Path, skill_name: str, description: str) -> bool:
    agents_dir = skill_dir / "agents"
    openai_yaml = agents_dir / "openai.yaml"
    if openai_yaml.exists():
        return False

    agents_dir.mkdir(parents=True, exist_ok=True)
    display_name = format_display_name(skill_name)
    short_desc = clamp_short_description(description, display_name)
    default_prompt = f"Use ${skill_name} to complete this request with a structured workflow."

    content = (
        "interface:\n"
        f"  display_name: {yaml_quote(display_name)}\n"
        f"  short_description: {yaml_quote(short_desc)}\n"
        f"  default_prompt: {yaml_quote(default_prompt)}\n"
    )
    openai_yaml.write_text(content)
    return True


def adapt_skill(skill_md: Path) -> tuple[bool, bool]:
    original = skill_md.read_text()
    frontmatter, body = parse_frontmatter(original)
    body, inline_description = pop_inline_description(body)

    skill_name = skill_md.parent.name
    changed_skill_md = False

    if frontmatter is None:
        frontmatter = {}
        changed_skill_md = True

    existing_name = frontmatter.get("name")
    if not isinstance(existing_name, str) or not existing_name.strip():
        frontmatter["name"] = skill_name
        changed_skill_md = True

    existing_description = frontmatter.get("description")
    if not isinstance(existing_description, str) or not existing_description.strip():
        frontmatter["description"] = inline_description or make_default_description(skill_name)
        changed_skill_md = True
    elif inline_description is not None:
        # Keep frontmatter as source of truth; remove inline duplicate.
        changed_skill_md = True

    # Ensure frontmatter order starts with name + description.
    ordered = {
        "name": frontmatter["name"],
        "description": frontmatter["description"],
    }
    for key, value in frontmatter.items():
        if key not in ordered:
            ordered[key] = value

    if changed_skill_md:
        frontmatter_text = yaml.safe_dump(ordered, sort_keys=False, allow_unicode=False).strip()
        body_out = body.lstrip("\n")
        updated = f"---\n{frontmatter_text}\n---\n\n{body_out}"
        if not updated.endswith("\n"):
            updated += "\n"
        skill_md.write_text(updated)

    changed_openai_yaml = ensure_openai_yaml(
        skill_md.parent,
        str(ordered["name"]).strip(),
        str(ordered["description"]).strip(),
    )
    return changed_skill_md, changed_openai_yaml


def main() -> None:
    skill_files = find_skill_files()
    if not skill_files:
        print("No SKILL.md files found.")
        return

    updated_skill_count = 0
    created_openai_yaml_count = 0

    for skill_md in skill_files:
        changed_skill_md, changed_openai_yaml = adapt_skill(skill_md)
        if changed_skill_md:
            updated_skill_count += 1
        if changed_openai_yaml:
            created_openai_yaml_count += 1

    print(f"Scanned skills: {len(skill_files)}")
    print(f"Updated SKILL.md: {updated_skill_count}")
    print(f"Created agents/openai.yaml: {created_openai_yaml_count}")


if __name__ == "__main__":
    main()
