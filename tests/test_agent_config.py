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


from src.agent import build_prompt


def test_bug_request_loads_investigate_bug_skill():
    prompt = build_prompt(
        "Please investigate BUG-456 and fix the failing test."
    )

    assert "Selected skill instructions:" in prompt
    assert "Retrieve the relevant ticket" in prompt


def test_review_request_loads_review_code_skill():
    prompt = build_prompt(
        "Please review this code for maintainability."
    )

    assert "Selected skill instructions:" in prompt
    assert "Review the code" in prompt


def test_unrelated_request_does_not_load_a_skill():
    prompt = build_prompt(
        "Explain how Python lists work."
    )

    assert "Selected skill instructions:" in prompt
    assert "Retrieve the relevant ticket" not in prompt
    assert "Review the code" not in prompt


def test_bug_prompt_contains_only_bug_tools():
    prompt = build_prompt(
        "Please investigate BUG-456 and fix the failing test."
    )

    tools_section = prompt.split(
        "Available tools for this task:",
        1
    )[1].split(
        "General rules:",
        1
    )[0]

    assert "get_ticket" in tools_section
    assert "run_tests" in tools_section
    assert "read_file" in tools_section
    assert "edit_file" in tools_section

    assert "search_files" not in tools_section
    assert "get_repository" not in tools_section


def test_review_prompt_contains_only_review_tools():
    prompt = build_prompt(
        "Please review this code for maintainability."
    )

    tools_section = prompt.split(
        "Available tools for this task:",
        1
    )[1].split(
        "General rules:",
        1
    )[0]

    assert "search_files" in tools_section
    assert "read_file" in tools_section

    assert "get_ticket" not in tools_section
    assert "run_tests" not in tools_section
    assert "edit_file" not in tools_section