
import json

POLICY = """
Customers may return unopened products within 30 days.

Opened products may be returned within 14 days
only if they are defective.

Digital products cannot be returned.

Refunds are issued to the original payment method.
"""


def load_golden_cases():
    with open("data/golden_cases.json", "r") as file:
        return json.load(file)


# def test_golden_cases_with_real_llm_judge():
#     load_dotenv()
#
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         raise ValueError("GEMINI_API_KEY was not found.")
#
#     client = genai.Client(api_key=api_key)
#
#     cases = load_golden_cases()
#
#     for case in cases:
#         evaluation = evaluate_response(
#             client=client,
#             policy=POLICY,
#             question="Can I return an unopened product after 20 days?",
#             ai_response=case["ai_response"],
#             evaluation_criteria=(
#                 "The AI should state that an unopened product purchased "
#                 "20 days ago can be returned because unopened products "
#                 "can be returned within 30 days."
#             )
#         )
#
#         print(f"\nGolden case {case['id']}")
#         print(f"AI response: {case['ai_response']}")
#         print(f"Expected judge evaluation: {case['expected_judge_evaluation']}")
#         print(f"Actual judge result: {evaluation.result}")
#         print(f"Judge reason: {evaluation.reason}")
#
#         assert evaluation.result == case["expected_judge_evaluation"]
#
#
