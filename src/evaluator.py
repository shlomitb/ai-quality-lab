from google.genai import types

from src.config import JUDGE_MODEL
from src.evaluation_result import EvaluationResult
from src.llm import ask_llm


def evaluate_response(
    client,
    policy,
    question,
    ai_response,
    evaluation_criteria,
    model=JUDGE_MODEL
):

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

    response = ask_llm(
        client=client,
        prompt=prompt,
        model=model,
        config=config
    )

    return response.parsed