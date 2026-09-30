# Standalone LLM-as-a-Judge — Learning Example

This is an earlier implementation of an LLM-as-a-judge system that I built
to understand how AI response evaluation works before using DeepEval.

The example demonstrates:

- Designing an evaluator prompt
- Using an LLM as a judge
- Asking the judge to evaluate an AI response against a policy and criteria
- Using Pydantic to define a structured evaluation response
- Using Google's structured JSON response support
- Separating evaluation logic from the application being evaluated

The project later evolved to use DeepEval for evaluation and metrics.
This code is preserved as a learning example and is not part of the
current production evaluation pipeline.