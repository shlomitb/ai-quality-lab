from google.genai import types

from src.llm import ask_llm
from src.tools import get_return_policy, get_product_information


def get_tool_calls(response):
    tool_calls = []

    for content in response.automatic_function_calling_history or []:
        for part in content.parts or []:
            if part.function_call is not None:
                tool_calls.append(part.function_call.name)

    return tool_calls

def answer_customer_with_trace(client, question):
    prompt = f"""
        You are a customer-support assistant.
    
        Answer the customer's question using the appropriate available tool.
    
        Customer question:
        {question}
    
        Available tools:
    
        - get_return_policy:
          Use this to retrieve the company's return policy and return rules.
    
        - get_product_information:
          Use this to retrieve information about the product, such as its
          name, category, or price.
    
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


