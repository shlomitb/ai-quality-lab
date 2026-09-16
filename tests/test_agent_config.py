from pathlib import Path


def test_agents_md_exists():
    agents_file = Path("AGENTS.md")

    assert agents_file.exists()


def test_load_agents_instructions():
    from src.agent import load_agents_instructions

    instructions = load_agents_instructions()

    assert "Run the relevant tests" in instructions
    assert "Do not report that a bug is fixed" in instructions