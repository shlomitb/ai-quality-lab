


"""
This file should know how to construct the customer-support prompt and call Gemini.

build customer-support prompt
    call_llm()
    return text
"""


#gemini-3.6-flash
#gemini-3.5-flash

def ask_llm(
    client,
    prompt,
    model="gemini-3.6-flash",
    config=None
):
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config
    )

    return response