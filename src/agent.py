from src.llm import ask_llm


"""
This agent defines what the customer-support agent does
"""

def answer_customer(client, policy, question):

    prompt = f"""
    You are a customer-support assistant.
    
    Answer the customer's question using ONLY the company return policy.
    
    Company policy:
    {policy}
    
    Customer question:
    {question}
    
    If the policy does not contain enough information to determine
    whether the customer is eligible for a return, ask the customer
    for the missing information instead of guessing.
    
    Give a clear and helpful answer.
    """

    response = ask_llm(
        client=client,
        prompt=prompt
    )

    return response.text