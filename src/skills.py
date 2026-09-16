from dataclasses import dataclass
from pathlib import Path



@dataclass
class SelectedSkill:
    name: str
    instructions: str
    tools: list[str]


SKILL_TOOLS = {
    "investigate-bug": [
        "get_ticket",
        "run_tests",
        "read_file",
        "edit_file",
    ],
    "review-code": [
        "search_files",
        "read_file",
    ],
}

EXTRA_TOOL_KEYWORDS = {
    "run_tests": [
        "run the tests",
        "run tests",
        "test it",
        "verify with tests",
    ],
}

SKILL_ESCALATION_TOOLS = {
    "investigate-bug": [
        "get_repository",
    ],
    "review-code": [
        "run_tests",
    ],
}


def load_skill_descriptions() -> str:
    skills_file = Path("skills/skills.md")

    if not skills_file.exists():
        return ""

    return skills_file.read_text()


def select_skill(question: str) -> str:
    """
    Select the skill with the most matching keywords
    from skills/skills.md.
    """
    question_lower = question.lower()
    skills_text = load_skill_descriptions()

    skills = {}
    current_skill = ""

    for line in skills_text.splitlines():
        line = line.strip()

        if line.startswith("## "):
            current_skill = line[3:].strip()
            skills[current_skill] = []

        elif line.startswith("- ") and current_skill:
            keyword = line[2:].strip().lower()
            skills[current_skill].append(keyword)

    best_skill = ""
    best_score = 0

    for skill_name, keywords in skills.items():
        score = sum(
            1
            for keyword in keywords
            if keyword in question_lower
        )

        best_skill = ""
        best_score = 0
        tie = False

        for skill_name, keywords in skills.items():
            score = sum(
                1
                for keyword in keywords
                if keyword in question_lower
            )

            if score > best_score:
                best_skill = skill_name
                best_score = score
                tie = False

            elif score == best_score and score > 0:
                tie = True

        if tie:
            return ""

        return best_skill

    return best_skill


def get_skill_instructions(question: str) -> str:
    skill_name = select_skill(question)

    if not skill_name:
        return ""

    return load_skill(skill_name)


def load_skill(skill_name: str) -> str:
    skill_file = Path("skills") / skill_name / "SKILL.md"

    if not skill_file.exists():
        return ""

    return skill_file.read_text()


def get_selected_skill(question: str) -> SelectedSkill | None:
    skill_name = select_skill(question)

    if not skill_name:
        return None

    tools = list(SKILL_TOOLS.get(skill_name, []))

    question_lower = question.lower()

    for tool_name, keywords in EXTRA_TOOL_KEYWORDS.items():
        if any(keyword in question_lower for keyword in keywords):
            if tool_name not in tools:
                tools.append(tool_name)

    return SelectedSkill(
        name=skill_name,
        instructions=load_skill(skill_name),

        tools=tools,
    )

def get_skill_info(question: str) -> tuple[str, int]:
    skill = get_selected_skill(question)

    if skill is None:
        return "", 0

    return skill.name, len(skill.instructions)


def is_tool_escalation_allowed(skill_name: str,tool_name: str,) -> bool:
    allowed_tools = SKILL_ESCALATION_TOOLS.get(skill_name, [])

    return tool_name in allowed_tools

