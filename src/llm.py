from llm_client import call_llm


"""
This file should know how to construct the customer-support prompt and call Gemini.

build customer-support prompt
    call_llm()
    return text
"""


#gemini-3.6-flash
#gemini-3.5-flash

def ask_llm(client, policy, question, model="gemini-3.6-flash"):

    prompt = f"""
    You are a customer-support assistant.
    
    Answer the customer's question using ONLY the company return policy.
    
    Company policy:
    {policy}
    
    Customer question:
    {question}
    """

    response = call_llm(
        client=client,
        model=model,
        prompt=prompt
    )

    return response.text