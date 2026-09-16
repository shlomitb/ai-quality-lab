from deepeval.tracing import observe, update_current_trace
from google.genai import types
from pathlib import Path

from src.llm import ask_llm
from src.tools import (
    get_return_policy,
    get_product_information,
    search_product_catalog,
    get_order_information,
    search_order_database,
    check_return_eligibility,
    update_order_status,
    get_ticket,
    get_repository,
    search_files,
    run_tests,
    edit_file,
    read_file,
)


def get_tool_calls(response):
    return [tool_call.name for tool_call in response.tool_calls]


def get_tool_call_details(response):
    return [
        {
            "name": tool_call.name,
            "args": tool_call.args,
        }
        for tool_call in response.tool_calls
    ]


def get_tool_result_details(response):
    return [
        {
            "name": tool_result.name,
            "response": tool_result.response,
        }
        for tool_result in response.tool_results
    ]


@observe(type="agent")
def answer_customer_with_trace(client, question):
    """Run the customer-support agent and return the full response."""
    agents_instructions = load_agents_instructions()
    skill_descriptions = load_skill_descriptions()

    selected_skill = ""

    if (
            "bug" in question.lower()
            or "fix" in question.lower()
            or "failing test" in question.lower()
    ):
        selected_skill = load_skill("investigate-bug")

    prompt = f"""
    You are a software-development assistant.

    Available skills:
    {skill_descriptions}
    
    Use the selected skill instructions below as the procedure
    for this task when a relevant skill has been selected.
    
    Selected skill instructions:
    {selected_skill}

    Investigate and respond to the user's request using the appropriate
    available tools.

    User request:
    {question}

    Available tools:

    - get_ticket:
      Use this to retrieve information about a specific ticket.
      It requires the ticket_id argument.

    - get_repository:
      Use this to retrieve information about a specific repository.
      It requires the repository_name argument.

    - search_files:
      Use this to search files in a repository for a specific term.
      It requires the repository_name and search_term arguments.

    - run_tests:
      Use this to run the test suite for a repository.
      It requires the repository_name argument.

    - edit_file:
      Use this to modify the contents of an existing file in a repository.
      It requires the repository_name, file_path, and new_content arguments.
      
    - read_file:
      Use this to read the contents of a specific file in a repository.
      It requires the repository_name and file_path arguments.

    General rules:

    - Choose only the tools that are relevant to the user's request.
    
    - Do not use tools unnecessarily.
    
    - When a tool returns information needed for a later step, use that
      information rather than making assumptions.
      
    - Do not claim that an action was completed unless the available
      tool results provide evidence that it was completed.
      
    - Do not make assumptions when the available information is insufficient.

    Return-policy rules:

    - Use get_return_policy only when the customer asks for the return
      policy or when the available order/eligibility information is
      insufficient to answer the question.
    - Do not call get_return_policy solely to explain an eligibility
      result that has already been determined.
    """

    config = types.GenerateContentConfig(
        tools=[
            get_return_policy,
            get_product_information,
            search_product_catalog,
            get_order_information,
            search_order_database,
            check_return_eligibility,
            update_order_status,
            get_ticket,
            get_repository,
            search_files,
            run_tests,
            edit_file,
            read_file,
        ]
    )

    response = ask_llm(
        client=client,
        prompt=prompt,
        config=config
    )

    update_current_trace(
        input=question,
        output=response.final_text,
    )

    return response




def answer_customer(client, question):
    response = answer_customer_with_trace(
        client=client,
        question=question
    )

    return response.final_text


def load_agents_instructions() -> str:
    agents_file = Path("AGENTS.md")

    if not agents_file.exists():
        return ""

    return agents_file.read_text()


def load_skill_descriptions() -> str:
    skills_file = Path("skills/skills.md")

    if not skills_file.exists():
        return ""

    return skills_file.read_text()


def load_skill(skill_name: str) -> str:
    skill_file = Path("skills") / skill_name / "SKILL.md"

    if not skill_file.exists():
        return ""

    return skill_file.read_text()






