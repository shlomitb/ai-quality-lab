from src.skills import select_skill, get_skill_instructions, get_selected_skill


def test_select_skill_for_bug():
    skill = select_skill(
        "Investigate BUG-456 and fix the failing test."
    )

    assert skill == "investigate-bug"


def test_select_skill_for_failing_test():
    skill = select_skill(
        "The failing test needs to be investigated."
    )

    assert skill == "investigate-bug"


def test_select_skill_when_no_skill_matches():
    skill = select_skill(
        "What is the weather today?"
    )

    assert skill == ""


def test_select_skill_from_skills_file():
    skill = select_skill(
        "Please investigate this bug and fix the failing test."
    )

    assert skill == "investigate-bug"


def test_select_skill_for_unrelated_question():
    skill = select_skill(
        "Explain how to connect to the database."
    )

    assert skill == ""


def test_select_skill_for_code_review():
    skill = select_skill(
        "Please review this code for bugs and maintainability."
    )

    assert skill == "review-code"


def test_select_skill_returns_no_skill_when_match_is_ambiguous():
    skill = select_skill(
        "Please review this bug."
    )

    assert skill == ""


def test_load_investigate_bug_skill():
    from src.skills import load_skill

    instructions = load_skill("investigate-bug")

    assert "Retrieve the relevant ticket" in instructions
    assert "run_tests" in instructions


def test_load_review_code_skill():
    from src.skills import load_skill

    instructions = load_skill("review-code")

    assert "Review the code for" in instructions
    assert "Do not modify the code unless" in instructions


def test_get_skill_instructions_for_bug():
    instructions = get_skill_instructions(
        "Please investigate this bug and fix the failing test."
    )

    assert "Retrieve the relevant ticket" in instructions


def test_get_skill_instructions_for_review():
    instructions = get_skill_instructions(
        "Please review this code for maintainability."
    )

    assert "Review the code" in instructions


def test_get_skill_instructions_for_unrelated_request():
    instructions = get_skill_instructions(
        "Explain Python lists."
    )

    assert instructions == ""


def test_get_selected_bug_skill():
    skill = get_selected_skill(
        "Investigate BUG-456 and fix the failing test."
    )

    assert skill is not None
    assert skill.name == "investigate-bug"
    assert "Retrieve the relevant ticket" in skill.instructions


def test_get_selected_review_skill():
    skill = get_selected_skill(
        "Please review this code for maintainability."
    )

    assert skill is not None
    assert skill.name == "review-code"
    assert "Review the code" in skill.instructions


def test_get_selected_skill_when_none_matches():
    skill = get_selected_skill(
        "Explain Python lists."
    )

    assert skill is None


def test_review_skill_includes_run_tests_when_explicitly_requested():
    skill = get_selected_skill(
        "Please review this code and run the tests to verify your findings."
    )

    assert skill is not None
    assert skill.name == "review-code"
    assert "search_files" in skill.tools
    assert "read_file" in skill.tools
    assert "run_tests" in skill.tools


def test_review_skill_can_escalate_to_run_tests():
    from src.skills import is_tool_escalation_allowed

    assert is_tool_escalation_allowed(
        "review-code",
        "run_tests",
    )


def test_review_skill_cannot_escalate_to_edit_file():
    from src.skills import is_tool_escalation_allowed

    assert not is_tool_escalation_allowed(
        "review-code",
        "edit_file",
    )


def test_unknown_tool_is_not_allowed():
    from src.skills import is_tool_escalation_allowed

    assert not is_tool_escalation_allowed(
        "review-code",
        "delete_database",
    )