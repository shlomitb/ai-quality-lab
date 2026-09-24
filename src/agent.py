
from deepeval.tracing import observe, update_current_trace
from google.genai import types
from pathlib import Path

from src.llm import create_provider
from src.providers.response import AgentResponse, ToolResult

from src.skills import (
    get_selected_skill,
    request_tool_access as authorize_tool_access_request,
    get_requestable_tools,
)

from src.tool_catalog import (
    get_tools,
    get_tool_descriptions,
    request_tool_access,
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

        if get_requestable_tools(selected_skill.name):
            prompt_tool_names.append("request_tool_access")

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


def get_authorized_tools(selected_skill):
    if selected_skill is None:
        return []

    tools = get_tools(selected_skill.tools)

    if get_requestable_tools(selected_skill.name):
        tools.append(request_tool_access)

    return tools


@observe(type="agent")
def answer_customer_with_trace(client, question):
    """Run the software-development agent and return the full response."""
    selected_skill = get_selected_skill(question)

    prompt = build_prompt(
        question,
        selected_skill,
    )

    provider = create_provider(
        client=client,
    )

    tools = get_authorized_tools(selected_skill)

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

    # Keep the complete trajectory across all model turns.
    all_tool_calls = list(response.tool_calls)
    all_tool_results = []

    for _ in range(MAX_AGENT_TURNS):

        if not response.tool_calls:
            break

        tool_results = []

        for tool_call in response.tool_calls:
            tool_result = execute_tool_call(
                tool_call=tool_call,
                available_tools=tools,
                selected_skill=selected_skill,
            )

            tool_results.append(tool_result)

        all_tool_results.extend(tool_results)

        # Tool access may have changed the available tools.
        tools = get_authorized_tools(selected_skill)

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

        # Keep tool calls from this later model turn too.
        all_tool_calls.extend(response.tool_calls)

    final_response = AgentResponse(
        final_text=response.final_text,
        tool_calls=all_tool_calls,
        tool_results=all_tool_results,
        parsed=response.parsed,
    )

    update_current_trace(
        input=question,
        output=final_response.final_text,
    )

    return final_response


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


@observe(type="tool")
def execute_tool_call(tool_call, available_tools, selected_skill):
    if tool_call.name == "request_tool_access":
        requested_tool = tool_call.args.get("tool_name")

        if not isinstance(requested_tool, str):
            return ToolResult(
                name="request_tool_access",
                response={
                    "error": "tool_name is required."
                },
                call_id=tool_call.call_id,
            )

        if selected_skill is None:
            return ToolResult(
                name="request_tool_access",
                response={
                    "tool_name": requested_tool,
                    "authorized": False,
                    "error": "No skill is selected.",
                },
                call_id=tool_call.call_id,
            )

        allowed = authorize_tool_access_request(
            selected_skill,
            requested_tool,
        )

        return ToolResult(
            name="request_tool_access",
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



