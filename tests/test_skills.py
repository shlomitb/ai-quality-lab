
"""
Tests the skill-selection and tool-access logic.
Verifies that the skill system selects and loads the correct skill and instructions,
that initial and requestable tools are configured correctly,
and that authorized or unauthorized tool-access requests are handled properly.
"""

from src.skills import (
    TOOL_ACCESS_POLICY,
    ToolAccessRequest,
    authorize_tool_access,
    get_initial_tools,
    get_requestable_tools,
    get_selected_skill,
    get_skill_instructions,
    is_tool_access_requestable,
    is_tool_authorized,
    load_skill,
    request_tool_access,
    select_skill,
)


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
    instructions = load_skill("investigate-bug")

    assert "Retrieve the relevant ticket" in instructions
    assert "run_tests" in instructions


def test_load_review_code_skill():
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
    assert skill.tools == [
        "get_ticket",
        "run_tests",
        "read_file",
        "edit_file",
    ]


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


def test_review_skill_does_not_initially_include_requestable_tool():
    skill = get_selected_skill(
        "Please review this code and run the tests to verify your findings."
    )

    assert skill is not None
    assert skill.name == "review-code"
    assert "search_files" in skill.tools
    assert "read_file" in skill.tools
    assert "run_tests" not in skill.tools


def test_review_skill_can_request_access_to_run_tests():
    assert is_tool_access_requestable(
        "review-code",
        "run_tests",
    )


def test_review_skill_cannot_request_access_to_edit_file():
    assert not is_tool_access_requestable(
        "review-code",
        "edit_file",
    )


def test_review_code_tool_access_policy():
    policy = TOOL_ACCESS_POLICY["review-code"]

    assert policy["initial_tools"] == [
        "search_files",
        "read_file",
    ]

    assert policy["requestable_tools"] == [
        "run_tests",
    ]


def test_unknown_tool_is_not_allowed():
    assert not is_tool_access_requestable(
        "review-code",
        "delete_database",
    )


def test_authorize_allowed_tool_access():
    request = ToolAccessRequest(
        skill_name="review-code",
        tool_name="run_tests",
    )

    assert authorize_tool_access(request)


def test_authorize_denied_tool_access():
    request = ToolAccessRequest(
        skill_name="review-code",
        tool_name="edit_file",
    )

    assert not authorize_tool_access(request)


def test_request_tool_access_adds_allowed_tool():
    skill = get_selected_skill(
        "Please review this code."
    )

    assert skill is not None
    assert "run_tests" not in skill.tools

    allowed = request_tool_access(
        skill,
        "run_tests",
    )

    assert allowed
    assert "run_tests" in skill.tools


def test_request_tool_access_rejects_unauthorized_tool():
    skill = get_selected_skill(
        "Please review this code."
    )

    assert skill is not None
    assert "edit_file" not in skill.tools

    allowed = request_tool_access(
        skill,
        "edit_file",
    )

    assert not allowed
    assert "edit_file" not in skill.tools


def test_review_code_initial_tools():
    assert get_initial_tools("review-code") == [
        "search_files",
        "read_file",
    ]


def test_review_code_requestable_tools():
    assert get_requestable_tools("review-code") == [
        "run_tests",
    ]


def test_requestable_tool_is_authorized():
    assert is_tool_authorized(
        "review-code",
        "run_tests",
    )


def test_unlisted_tool_is_not_authorized():
    assert not is_tool_authorized(
        "review-code",
        "edit_file",
    )



def test_select_skill_chooses_skill_with_most_keyword_matches():
    skill = select_skill(
        "Please review the code and investigate this bug and error."
    )

    assert skill == "investigate-bug"


def test_investigate_bug_initial_tools():
    assert get_initial_tools("investigate-bug") == [
        "get_ticket",
        "run_tests",
        "read_file",
        "edit_file",
    ]


def test_investigate_bug_requestable_tools():
    assert get_requestable_tools("investigate-bug") == [
        "get_repository",
    ]



def test_investigate_bug_requestable_tool_is_authorized():
    assert is_tool_authorized(
        "investigate-bug",
        "get_repository",
    )


def test_investigate_bug_unlisted_tool_is_not_authorized():
    assert not is_tool_authorized(
        "investigate-bug",
        "search_files",
    )


def test_initial_tool_cannot_be_requested_as_additional_access():
    assert not is_tool_access_requestable(
        "review-code",
        "read_file",
    )


def test_request_tool_access_does_not_duplicate_tool():
    skill = get_selected_skill(
        "Please review this code."
    )

    assert skill is not None

    assert request_tool_access(skill, "run_tests")
    assert request_tool_access(skill, "run_tests")

    assert skill.tools.count("run_tests") == 1


def test_get_initial_tools_returns_empty_for_unknown_skill():
    assert get_initial_tools("does-not-exist") == []


def test_get_requestable_tools_returns_empty_for_unknown_skill():
    assert get_requestable_tools("does-not-exist") == []


def test_unknown_skill_cannot_authorize_tool():
    assert not is_tool_authorized(
        "does-not-exist",
        "read_file",
    )


def test_unknown_skill_cannot_request_tool_access():
    assert not is_tool_access_requestable(
        "does-not-exist",
        "run_tests",
    )