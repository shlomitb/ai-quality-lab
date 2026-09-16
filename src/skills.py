from pathlib import Path


def load_skill_descriptions() -> str:
    skills_file = Path("skills/skills.md")

    if not skills_file.exists():
        return ""

    return skills_file.read_text()


def select_skill(question: str) -> str:
    question_lower = question.lower()
    skills_text = load_skill_descriptions()

    current_skill = ""

    for line in skills_text.splitlines():
        line = line.strip()

        if line.startswith("## "):
            current_skill = line[3:].strip()

        elif line.startswith("- ") and current_skill:
            keyword = line[2:].strip().lower()

            if keyword in question_lower:
                return current_skill

    return ""


def load_skill(skill_name: str) -> str:
    skill_file = Path("skills") / skill_name / "SKILL.md"

    if not skill_file.exists():
        return ""

    return skill_file.read_text()