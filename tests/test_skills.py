from src.skills import select_skill


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