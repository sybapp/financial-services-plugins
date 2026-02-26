#!/usr/bin/env python3
"""
Install repository skills into a Codex skills directory.

By default this copies all skills into ~/.codex/skills.
Use --link to create symlinks instead (useful during local development).
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


def find_skill_dirs() -> list[Path]:
    skills = {
        path.parent
        for path in ROOT_DIR.glob("**/skills/**/SKILL.md")
        if ".git" not in path.parts and ".codex" not in path.parts
    }
    return sorted(skills)


def build_destination_names(skill_dirs: list[Path]) -> dict[Path, str]:
    name_to_count: dict[str, int] = {}
    mapping: dict[Path, str] = {}

    for skill_dir in skill_dirs:
        skill_name = skill_dir.name
        name_to_count[skill_name] = name_to_count.get(skill_name, 0) + 1

    for skill_dir in skill_dirs:
        skill_name = skill_dir.name
        if name_to_count[skill_name] == 1:
            mapping[skill_dir] = skill_name
            continue

        rel = skill_dir.relative_to(ROOT_DIR)
        namespace = str(rel).split("/skills/", 1)[0].replace("/", "-")
        mapping[skill_dir] = f"{namespace}--{skill_name}"

    return mapping


def install_skill(src: Path, dst: Path, use_links: bool) -> None:
    if dst.exists() or dst.is_symlink():
        if dst.is_symlink() or dst.is_file():
            dst.unlink()
        else:
            shutil.rmtree(dst)

    if use_links:
        dst.symlink_to(src)
    else:
        shutil.copytree(src, dst)


def main() -> None:
    parser = argparse.ArgumentParser(description="Install this repo's skills into Codex skills home.")
    parser.add_argument(
        "--target",
        default="~/.codex/skills",
        help="Target skills directory (default: ~/.codex/skills)",
    )
    parser.add_argument(
        "--link",
        action="store_true",
        help="Create symlinks instead of copying files",
    )
    args = parser.parse_args()

    target_dir = Path(args.target).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    skill_dirs = find_skill_dirs()
    name_map = build_destination_names(skill_dirs)

    for src in skill_dirs:
        dest_name = name_map[src]
        dest = target_dir / dest_name
        install_skill(src, dest, args.link)
        mode = "linked" if args.link else "copied"
        print(f"{mode}: {src.relative_to(ROOT_DIR)} -> {dest}")

    print(f"\nInstalled {len(skill_dirs)} skills to {target_dir}")


if __name__ == "__main__":
    main()
