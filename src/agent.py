
from deepeval.tracing import observe, update_current_trace
from google.genai import types
from pathlib import Path

from src.llm import create_provider
from src.providers.response import AgentResponse, ToolResult
from src.security import sanitize_tool_result, sanitize_ticket, redact_sensitive_values

from src.skills import (
    TOOL_ACCESS_POLICY,
    get_selected_skill,
    request_tool_access as authorize_tool_access_request,
    get_requestable_tools,
    is_tool_permitted_by_policy,
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

    requestable_tool_names = []

    if selected_skill:
        selected_skill_instructions = selected_skill.instructions

        prompt_tool_names = list(selected_skill.tools)

        requestable_tool_names = get_requestable_tools(selected_skill.name)

        if requestable_tool_names:
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

        Requestable tools:
        {", ".join(requestable_tool_names) if requestable_tool_names else "None"}

        You may request access only to these tools.
        Do not invent or guess other tool names.
        If a tool request is denied, do not try alternative tool names.

        General rules:

        - Choose only the tools that are relevant to the user's request.
        - Do not use tools unnecessarily.
        - When a tool returns information needed for a later step, use that
          information rather than making assumptions.
        - Do not claim that an action was completed unless the available
          tool results provide evidence that it was completed.
        - Do not make assumptions when the available information is insufficient.
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

    print("TOOLS REQUESTED:", selected_skill.tools)

    tools = get_tools(selected_skill.tools)

    print("TOOLS FROM get_tools:", [tool.__name__ for tool in tools])

    if get_requestable_tools(selected_skill.name):
        tools.append(request_tool_access)

    return tools


def enforce_tool_result_consistency(response):
    """
    Prevent the agent from reporting successful test verification
    when the latest run_tests result shows failure.
    """
    for tool_result in reversed(response.tool_results):
        if tool_result.name != "run_tests":
            continue

        result = tool_result.response

        status = (
            result.get("result", {})
            .get("result", {})
            .get("status")
        )

        if status == "failed":
            return AgentResponse(
                final_text=(
                    "The tests failed, so I cannot report the "
                    "verification as successful."
                ),
                tool_calls=response.tool_calls,
                tool_results=response.tool_results,
                parsed=response.parsed,
            )

        if status == "passed":
            break

    return response


@observe(type="agent")
def answer_customer_with_trace(client, question):
    """Run the software-development agent and return the full response."""
    selected_skill = get_selected_skill(question)

    print("SELECTED SKILL:", selected_skill.name if selected_skill else None)
    print("SKILL TOOLS:", selected_skill.tools if selected_skill else None)

    prompt = build_prompt(
        question,
        selected_skill,
    )

    provider = create_provider(
        client=client,
    )

    tools = get_authorized_tools(selected_skill)

    print("AUTHORIZED TOOLS:", [tool.__name__ for tool in tools])

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

    if response.tool_calls:
        final_text = (
            "I could not complete the request because the agent "
            "reached its maximum number of turns."
        )
    else:
        final_text = response.final_text

    final_response = AgentResponse(
        final_text=final_text,
        tool_calls=all_tool_calls,
        tool_results=all_tool_results,
        parsed=response.parsed,
    )

    final_response = enforce_tool_result_consistency(final_response)

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



def _handle_tool_access_request(tool_call, selected_skill):
    """Authorize a request for an additional tool."""

    requested_tool = tool_call.args.get("tool_name")

    if not isinstance(requested_tool, str) or not requested_tool:
        return ToolResult(
            name=tool_call.name,
            response={"error": "tool_name is required."},
            call_id=tool_call.call_id,
        )

    policy = TOOL_ACCESS_POLICY.get(selected_skill.name)

    if policy is None:
        return ToolResult(
            name=tool_call.name,
            response={
                "error": (
                    f"No tool access policy for skill "
                    f"'{selected_skill.name}'."
                )
            },
            call_id=tool_call.call_id,
        )

    if requested_tool not in policy["requestable_tools"]:
        return ToolResult(
            name=tool_call.name,
            response={
                "tool_name": requested_tool,
                "authorized": False,
            },
            call_id=tool_call.call_id,
        )

    if requested_tool not in selected_skill.tools:
        selected_skill.tools.append(requested_tool)

    return ToolResult(
        name=tool_call.name,
        response={
            "tool_name": requested_tool,
            "authorized": True,
        },
        call_id=tool_call.call_id,
    )


def _find_tool(tool_name, available_tools):
    """Return the available tool with the requested name."""
    return next(
        (
            tool
            for tool in available_tools
            if tool.__name__ == tool_name
        ),
        None,
    )


def _sanitize_tool_result(tool_name, response):
    """Sanitize a tool result before returning it to the agent."""

    if tool_name == "get_ticket":
        if (
            isinstance(response, dict)
            and isinstance(response.get("result"), dict)
        ):
            response["result"] = sanitize_ticket(response["result"])
            return response

    return redact_sensitive_values(response)


@observe(type="tool")
def execute_tool_call(tool_call, available_tools, selected_skill):
    """Execute a tool call only when authorized by the selected skill."""

    if selected_skill is None:
        return ToolResult(
            name=tool_call.name,
            response={
                "error": "No skill is selected; tool access denied."
            },
            call_id=tool_call.call_id,
        )

    if tool_call.name == "request_tool_access":
        return _handle_tool_access_request(
            tool_call,
            selected_skill,
        )

    if tool_call.name not in selected_skill.tools:
        return ToolResult(
            name=tool_call.name,
            response={
                "error": (
                    f"Tool '{tool_call.name}' is not authorized "
                    f"for skill '{selected_skill.name}'."
                )
            },
            call_id=tool_call.call_id,
        )

    tool = _find_tool(
        tool_call.name,
        available_tools,
    )

    if tool is None:
        return ToolResult(
            name=tool_call.name,
            response={
                "error": f"Tool '{tool_call.name}' is not available."
            },
            call_id=tool_call.call_id,
        )

    try:
        response = tool(**tool_call.args)
    except Exception as exc:
        return ToolResult(
            name=tool_call.name,
            response={"error": str(exc)},
            call_id=tool_call.call_id,
        )

    response = _sanitize_tool_result(
        tool_call.name,
        response,
    )

    return ToolResult(
        name=tool_call.name,
        response=response,
        call_id=tool_call.call_id,
    )


def handle_tool_access_request(tool_call, selected_skill):
    requested_tool = tool_call.args.get("tool_name")

    if not isinstance(requested_tool, str):
        return ToolResult(
            name="request_tool_access",
            response={
                "error": "tool_name is required.",
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


def is_tool_authorized_for_skill(tool_name, selected_skill):
    if selected_skill is None:
        return False

    return is_tool_permitted_by_policy(
        selected_skill.name,
        tool_name,
    )


def filter_sensitive_information(response):
    sensitive_values = {
        "INTERNAL-ONLY-12345",
    }

    filtered_text = response.final_text

    for sensitive_value in sensitive_values:
        filtered_text = filtered_text.replace(
            sensitive_value,
            "[REDACTED]",
        )

    return AgentResponse(
        final_text=filtered_text,
        tool_calls=response.tool_calls,
        tool_results=response.tool_results,
        parsed=response.parsed,
    )
