
from deepeval.tracing import observe, update_current_trace
from google.genai import types
from pathlib import Path

from src.llm import create_provider
from src.providers.response import ToolCall,ToolResult
from src.skills import (
    get_selected_skill,
    AUTHORIZED_ESCALATION_TOOLS,
    request_tool_escalation as apply_tool_escalation,
)

from src.tool_catalog import (
    get_tools,
    get_tool_descriptions,
    request_tool_escalation,
)

MAX_AGENT_TURNS = 10

def get_tool_calls(response):
    return [tool_call.name for tool_call in response.tool_calls]


def get_tool_call_details(response):
    return [
        {
            "name": tool_call.name,
            "args": tool_call.args,
            "call_id": tool_call.call_id,
        }
        for tool_call in response.tool_calls
    ]


def build_prompt(question: str, selected_skill=None) -> str:
    agents_instructions = load_agents_instructions()
    skill_descriptions = load_skill_descriptions()

    if selected_skill is None:
        selected_skill = get_selected_skill(question)

    if selected_skill:
        selected_skill_instructions = selected_skill.instructions

        prompt_tool_names = list(selected_skill.tools)

        if selected_skill.name in AUTHORIZED_ESCALATION_TOOLS:
            prompt_tool_names.append("request_tool_escalation")

        tool_descriptions = get_tool_descriptions(prompt_tool_names)
    else:
        selected_skill_instructions = ""
        tool_descriptions = ""

    prompt = f"""
        You are a software-development assistant.

        Repository instructions:
        {agents_instructions}

        Available skills:
        {skill_descriptions}

        Selected skill:
        {selected_skill.name if selected_skill else "None"}

        Selected skill instructions:
        {selected_skill_instructions}

        Investigate and respond to the user's request using the appropriate
        available tools.

        User request:
        {question}

        Available tools for this task:

        {tool_descriptions}

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

    return prompt


def get_tool_result_details(response):
    return [
        {
            "name": tool_result.name,
            "response": tool_result.response,
            "call_id": tool_result.call_id,
        }
        for tool_result in response.tool_results
    ]



@observe(type="agent")
def answer_customer_with_trace(client, question):
    """Run the software-development agent and return the full response."""

    selected_skill = get_selected_skill(question)

    prompt = build_prompt(
        question,
        selected_skill,
    )

    provider = create_provider(client=client)

    if selected_skill:
        tools = get_tools(selected_skill.tools)

        if selected_skill.name in AUTHORIZED_ESCALATION_TOOLS:
            tools.append(request_tool_escalation)
    else:
        tools = []

    config = types.GenerateContentConfig(
        tools=tools,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    )

    response = provider.generate(
        prompt=prompt,
        config=config,
    )

    for _ in range(MAX_AGENT_TURNS):

        if not response.tool_calls:
            break

        tool_results = []

        for tool_call in response.tool_calls:
            result = execute_tool_call(
                tool_call=tool_call,
                available_tools=tools,
                selected_skill=selected_skill,
            )

            tool_results.append(result)

        if selected_skill:
            tools = get_tools(selected_skill.tools)

            if selected_skill.name in AUTHORIZED_ESCALATION_TOOLS:
                tools.append(request_tool_escalation)
        else:
            tools = []

        config = types.GenerateContentConfig(
            tools=tools,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        )

        response = provider.send_tool_results(
            tool_results=tool_results,
            config=config,
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


def execute_tool_call(tool_call, available_tools, selected_skill):
    if tool_call.name == "request_tool_escalation":
        requested_tool = tool_call.args.get("tool_name")

        if not isinstance(requested_tool, str):
            return ToolResult(
                name="request_tool_escalation",
                response={
                    "error": "tool_name is required."
                },
                call_id=tool_call.call_id,
            )

        if selected_skill is None:
            return ToolResult(
                name="request_tool_escalation",
                response={
                    "tool_name": requested_tool,
                    "authorized": False,
                    "error": "No skill is selected.",
                },
                call_id=tool_call.call_id,
            )

        allowed = apply_tool_escalation(
            selected_skill,
            requested_tool,
        )

        return ToolResult(
            name="request_tool_escalation",
            response={
                "tool_name": requested_tool,
                "authorized": allowed,
            },
            call_id=tool_call.call_id,
        )

    tool_map = {
        tool.__name__: tool
        for tool in available_tools
    }

    tool = tool_map.get(tool_call.name)

    if tool is None:
        return ToolResult(
            name=tool_call.name,
            response={
                "error": "Tool is not available."
            },
            call_id=tool_call.call_id,
        )

    try:
        result = tool(**tool_call.args)

        return ToolResult(
            name=tool_call.name,
            response={
                "result": result,
            },
            call_id=tool_call.call_id,
        )

    except Exception as exc:
        return ToolResult(
            name=tool_call.name,
            response={
                "error": str(exc),
            },
            call_id=tool_call.call_id,
        )



