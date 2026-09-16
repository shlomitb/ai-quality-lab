from pathlib import Path


def test_agents_md_exists():
    agents_file = Path("AGENTS.md")

    assert agents_file.exists()


def test_load_agents_instructions():
    from src.agent import load_agents_instructions

    instructions = load_agents_instructions()

    assert "Run the relevant tests" in instructions
    assert "Do not report that a bug is fixed" in instructions


def test_investigate_bug_skill_exists():
    from pathlib import Path

    skill_file = Path("skills/investigate-bug/SKILL.md")

    assert skill_file.exists()


def test_skills_description_exists():
    from pathlib import Path

    skills_file = Path("skills/skills.md")

    assert skills_file.exists()