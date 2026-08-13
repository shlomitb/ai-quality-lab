import json
import os

from google import genai


from llm_client import call_llm
"""
This file should know how to construct the customer-support prompt and call Gemini.

build customer-support prompt
    call_llm()
    return text
"""




def ask_llm(client, policy, question):
    prompt = f"""
        You are a customer-support assistant.
        
        Answer the customer's question using ONLY the company return policy.
        
        Company policy:
        {policy}
        
        Customer question:
        {question}
    """
    #gemini-3.6-flash
    #gemini-3.5-flash
    response = call_llm(
        client=client,
        model="gemini-3.5-flash-lite",
        prompt=prompt
    )

    return response.text