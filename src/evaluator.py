"""
    Requirement: Handling insufficient information

    When the policy does not contain enough information
    to determine an answer:

    1. The AI must not make an unsupported assumption.
    2. The AI must explain what information is missing.
    3. The AI must ask the customer for the missing information.

    Simple keyword matching is not a reliable enough way to test for AI evaluation.
    Since the response could contain a keyword phrase that is in a different context, when the response may be good.
"""


CLARIFICATION_KEYWORDS = [
    "need to know",
    "more information",
    "please tell me",
    "could you tell me",
]

def evaluate_behavior(response, expected_behavior):
    """
    checks for keywords in response and if they appear returns ask for clarification instead of the answer

    can make mistakes if a keyword phrase is found in the response but the meaning is different.
    :param response:
    :param expected_behavior:
    :return:
    """
    for phrase in CLARIFICATION_KEYWORDS:
        if phrase in response.lower():
            return "ask_for_clarification"
    return "answer"

def evaluate_behavior_with_llm(
    client,
    policy,
    question,
    ai_response,
    expected_behavior
):
    prompt = f"""
    You are an AI quality evaluator.

    Determine whether the AI response demonstrates
    the expected behavior.

    Company policy:
    {policy}

    Customer question:
    {question}

    AI response:
    {ai_response}

    Expected behavior:
    {expected_behavior}

    Return only:
    PASS
    or
    FAIL
    """

    result = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    return result.text.strip()


def evaluate_response(client, policy, question, ai_response, evaluation_criteria):
    """
    The second llm call will judge the response of the first llm call
    """

    prompt = f"""
    You are an AI quality evaluator.

    Evaluate the AI response using ONLY the company policy
    and the evaluation criteria provided below.

    Company policy:
    {policy}

    Customer question:
    {question}

    AI response:
    {ai_response}

    Evaluation criteria:
    {evaluation_criteria}

    Determine whether the AI response is consistent with
    the company policy and satisfies the evaluation criteria.

    Do not penalize the AI response for using different wording
    from the evaluation criteria if the meaning is correct.

    Return only one of these:
    PASS
    FAIL
    """


    # print("prompt: ", prompt)

    result = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    # return result.text.strip()

    print("JUDGE RESPONSE:", repr(result.text))
    return result.text.strip()



def main():
    print(evaluate_behavior(
        "I need to know whether the product is opened.",
        "ask_for_clarification"
    ))

    print(evaluate_behavior(
        "Yes, you can return the unopened product within 30 days.",
        "answer"
    ))

    print(evaluate_behavior(
        "Could you tell me whether the product is defective?",
        "ask_for_clarification"
    ))


if __name__ == "__main__":
    main()