from google.genai import types

from evaluation_result import EvaluationResult
from llm_client import call_llm
"""

LLM judge

    build evaluation prompt
    configure structured output
    call_llm()
    return EvaluationResult

"""

def evaluate_response(
    client,
    policy,
    question,
    ai_response,
    evaluation_criteria
):
    """
    Use an LLM judge to evaluate an AI response.

    The judge evaluates the response using only the
    company policy and evaluation criteria.
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
    
    Return a structured evaluation containing:
    - result: "PASS" or "FAIL"
    - reason: a brief explanation of why the response passed or failed
    """

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=EvaluationResult,
    )

    # gemini-3.6-flash
    # gemini-3.5-flash
    result = call_llm(
        client=client,
        model="gemini-3.5-flash-lite",
        prompt=prompt,
        config=config
    )

    return result.parsed
