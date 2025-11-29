"""Validate SKILL.md frontmatter across all skills."""

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent


def iter_skills():
    for path in ROOT.iterdir():
        skill_file = path / "SKILL.md"
        if skill_file.is_file():
            yield path, skill_file


def load_frontmatter(skill_file: Path) -> dict:
    lines = skill_file.read_text().splitlines()
    assert lines and lines[0].strip() == "---", f"{skill_file} missing frontmatter start"
    try:
        end = lines[1:].index("---") + 1
    except ValueError:  # pragma: no cover - explicit assert below
        assert False, f"{skill_file} missing closing frontmatter delimiter"
    meta = yaml.safe_load("\n".join(lines[1:end]))
    assert isinstance(meta, dict), f"{skill_file} frontmatter is not a mapping"
    return meta


def test_frontmatter_parses_and_matches_folder():
    for folder, skill_file in iter_skills():
        meta = load_frontmatter(skill_file)
        assert "name" in meta, f"{skill_file} frontmatter missing name"
        assert meta["name"] == folder.name, (
            f"Frontmatter name '{meta['name']}' does not match folder '{folder.name}'"
        )
