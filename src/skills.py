from dataclasses import dataclass
from pathlib import Path



@dataclass
class SelectedSkill:
    name: str
    instructions: str
    tools: list[str]


@dataclass
class ToolAccessRequest:
    skill_name: str
    tool_name: str


TOOL_ACCESS_POLICY = {
    "investigate-bug": {
        "initial_tools": [
            "get_ticket",
            "run_tests",
            "read_file",
            "edit_file",
        ],
        "requestable_tools": [
            "get_repository",
        ],
    },
    "review-code": {
        "initial_tools": [
            "search_files",
            "read_file",
        ],
        "requestable_tools": [
            "run_tests",
        ],
    },
}


def get_initial_tools(skill_name: str) -> list[str]:
    policy = TOOL_ACCESS_POLICY.get(skill_name, {})
    return list(policy.get("initial_tools", []))


def get_requestable_tools(skill_name: str) -> list[str]:
    policy = TOOL_ACCESS_POLICY.get(skill_name, {})
    return list(policy.get("requestable_tools", []))


def is_tool_authorized(skill_name: str, tool_name: str) -> bool:
    policy = TOOL_ACCESS_POLICY.get(skill_name, {})

    return (
        tool_name in policy.get("initial_tools", [])
        or tool_name in policy.get("requestable_tools", [])
    )


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

    tools =  get_initial_tools(skill_name)

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


def is_tool_access_allowed(skill_name: str, tool_name: str, ) -> bool:
    allowed_tools = get_requestable_tools(skill_name)
    return tool_name in allowed_tools


def authorize_tool_access(request: ToolAccessRequest, ) -> bool:
    return is_tool_access_allowed(
        request.skill_name,
        request.tool_name,
    )


def request_tool_access(skill: SelectedSkill, tool_name: str, ) -> bool:
    request = ToolAccessRequest(
        skill_name=skill.name,
        tool_name=tool_name,
    )

    if not authorize_tool_access(request):
        return False

    if tool_name not in skill.tools:
        skill.tools.append(tool_name)

    return True