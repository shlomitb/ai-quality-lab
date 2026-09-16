from src.agent import build_prompt


def test_show_bug_skill_prompt():
    prompt = build_prompt(
        "Please investigate BUG-456 and fix the failing test."
    )

    print("\n" + "=" * 70)
    print("BUG REQUEST")
    print("=" * 70)
    print(prompt)
    print("=" * 70)


def test_show_review_skill_prompt():
    prompt = build_prompt(
        "Please review this code for maintainability."
    )

    print("\n" + "=" * 70)
    print("REVIEW REQUEST")
    print("=" * 70)
    print(prompt)
    print("=" * 70)