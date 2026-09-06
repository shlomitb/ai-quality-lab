from google.genai import types

from src.llm import ask_llm
from src.tools import get_return_policy, get_product_information


def get_tool_calls(response):
    """Return the names of tools called during the agent run."""
    tool_calls = []

    for content in response.automatic_function_calling_history or []:
        for part in content.parts or []:
            if part.function_call is not None:
                tool_calls.append(part.function_call.name)

    return tool_calls

def get_tool_call_details(response):
    """Return tool names and arguments from the agent run."""
    tool_calls = []

    for content in response.automatic_function_calling_history or []:
        for part in content.parts or []:
            if part.function_call is not None:
                tool_calls.append(
                    {
                        "name": part.function_call.name,
                        "args": part.function_call.args,
                    }
                )

    return tool_calls


def get_tool_result_details(response):
    """Return tool names and results from the agent run."""
    tool_results = []

    for content in response.automatic_function_calling_history or []:
        for part in content.parts or []:
            function_response = getattr(part, "function_response", None)

            if function_response is not None:
                tool_results.append(
                    {
                        "name": function_response.name,
                        "response": function_response.response,
                    }
                )

    return tool_results


def answer_customer_with_trace(client, question):
    """Run the customer-support agent and return the full response."""
    prompt = f"""
        You are a customer-support assistant.
    
        Answer the customer's question using the appropriate available tool.
    
        Customer question:
        {question}
    
        Available tools:
    
        - get_return_policy:
          Use this to retrieve the company's return policy and return rules.
    
        - get_product_information:
          Use this to retrieve information about a specific product.
          It requires the product_name argument
    
        Choose the tool or tools that are relevant to the customer's question.
        Do not use a tool unnecessarily.
    
        If the question does not contain enough information to determine
        whether the customer is eligible for a return, ask for the specific
        missing information.
    
        Do not make assumptions.
        Do not give a list of possible outcomes instead of asking for
        the missing information.
        """

    config = types.GenerateContentConfig(
        tools=[
            get_return_policy,
            get_product_information,
        ]
    )

    response = ask_llm(
        client=client,
        prompt=prompt,
        config=config
    )

    return response




def answer_customer(client, question):
    response = answer_customer_with_trace(
        client=client,
        question=question
    )

    return response.text


