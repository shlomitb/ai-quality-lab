from google.genai import types

from src.llm import ask_llm
from src.tools import get_return_policy

def answer_customer(client, question):

    prompt = f"""
    You are a customer-support assistant.
    
    Answer the customer's question using the company's return policy.
    
    Customer question:
    {question}
    
    If you need the return policy to answer the question,
    use the get_return_policy tool.
    
    If the customer's question does not contain enough information
    to determine whether they are eligible for a return, ask for
    the specific missing information.
    
    Do not make assumptions.
    Do not give a list of possible outcomes instead of asking
    for the missing information.
    """

    config = types.GenerateContentConfig(
        tools=[get_return_policy]
    )

    response = ask_llm(
        client=client,
        prompt=prompt,
        config=config
    )

    return response.text