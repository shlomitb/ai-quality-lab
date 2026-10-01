"""
Tests the agent's configuration and prompt construction.
Verifies that skills, instructions, tools, and the dynamic tool-access mechanism are correctly included in the prompt for each type of request.
"""


from pathlib import Path
from src.agent import build_prompt, load_agents_instructions


def test_agents_md_exists():
    agents_file = Path("AGENTS.md")

    assert agents_file.exists()


def test_load_agents_instructions():
    instructions = load_agents_instructions()

    assert "Run the relevant tests" in instructions
    assert "Do not report that a bug is fixed" in instructions


def test_investigate_bug_skill_exists():
    skill_file = Path("skills/investigate-bug/SKILL.md")

    assert skill_file.exists()


def test_skills_description_exists():
    skills_file = Path("skills/skills.md")

    assert skills_file.exists()


def test_bug_request_loads_investigate_bug_skill():
    prompt = build_prompt(
        "Please investigate BUG-456 and fix the failing test."
    )

    selected_skill = prompt.split(
        "Selected skill:",
        1
    )[1].split(
        "Selected skill instructions:",
        1
    )[0].strip()

    assert selected_skill == "investigate-bug"


def test_review_request_loads_review_code_skill():
    prompt = build_prompt(
        "Please review this code for maintainability."
    )

    assert "Selected skill instructions:" in prompt
    assert "Review the code" in prompt


def test_unrelated_request_does_not_load_a_skill():
    prompt = build_prompt(
        "What is the weather today?"
    )

    selected_skill = prompt.split(
        "Selected skill:",
        1
    )[1].split(
        "Selected skill instructions:",
        1
    )[0].strip()

    assert selected_skill == "None"


def test_bug_prompt_contains_initial_bug_tools_and_access_tool():
    prompt = build_prompt(
        "Please investigate BUG-456 and fix the failing test."
    )

    tools_section = prompt.split(
        "Available tools for this task:",
        1
    )[1].split(
        "Requestable tools:",
        1
    )[0]

    assert "get_ticket" in tools_section
    assert "run_tests" in tools_section
    assert "read_file" in tools_section
    assert "edit_file" in tools_section
    assert "request_tool_access" in tools_section

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
        "Requestable tools:",
        1
    )[0]

    assert "search_files" in tools_section
    assert "read_file" in tools_section

    assert "get_ticket" not in tools_section
    assert "run_tests" not in tools_section
    assert "edit_file" not in tools_section


def test_review_prompt_contains_initial_review_tools():
    prompt = build_prompt(
        "Please review this code."
    )

    tools_section = prompt.split(
        "Available tools for this task:",
        1
    )[1].split(
        "General rules:",
        1
    )[0]

    assert "request_tool_access" in tools_section


def test_access_tool_description_is_in_prompt():
    prompt = build_prompt(
        "Please review this code."
    )

    assert "The application will check whether the requested tool is authorized." in prompt