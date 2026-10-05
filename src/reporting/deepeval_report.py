import json
from pathlib import Path

from .models import DeepEvalMetricResult, DeepEvalTestResult


def load_deepeval_results(
    report_path: str | Path,
) -> list[DeepEvalTestResult]:
    """
    Read a DeepEval JSON run and convert it into normalized results.
    """

    report_path = Path(report_path)

    if not report_path.exists():
        raise FileNotFoundError(
            f"DeepEval report not found: {report_path}"
        )

    with report_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    results = []

    test_run_data = data.get("testRunData")

    if test_run_data is not None:
        test_cases = test_run_data.get("testCases", [])
    else:
        test_cases = data.get("testCases", [])

    for test_case in test_cases:
        metrics = []

        for metric in test_case.get("metricsData", []):
            score = metric.get("score")
            metrics.append(
                DeepEvalMetricResult(
                    name=metric["name"],
                    score=float(score) if score is not None else None,
                    threshold=float(metric["threshold"]),
                    success=bool(metric["success"]),
                    reason=metric.get("reason", ""),
                    evaluation_model=metric.get("evaluationModel"),
                    evaluation_cost=metric.get("evaluationCost"),
                    input_tokens=metric.get("inputTokenCount"),
                    output_tokens=metric.get("outputTokenCount"),
                )
            )
            print("\nDEEPEVAL METRIC:")
            print(metric)

        trajectory = []

        trace = test_case.get("trace", {})
        agent_spans = trace.get("agentSpans", [])

        if agent_spans:
            tools_called = agent_spans[0].get("toolsCalled", [])

            for tool_call in tools_called:
                output = tool_call.get("output", {})
                name = output.get("name")

                if name == "request_tool_access":
                    tool_name = (
                        tool_call
                        .get("inputParameters", {})
                        .get("tool_call", {})
                        .get("args", {})
                        .get("tool_name")
                    )

                    trajectory.append(
                        f"request_tool_access({tool_name})"
                    )
                elif name:
                    trajectory.append(name)

        results.append(
            DeepEvalTestResult(
                name=test_case["name"],
                success=bool(test_case["success"]),
                actual_output=test_case.get(
                    "actualOutput",
                    "",
                ),
                duration_seconds=float(
                    test_case.get("runDuration", 0.0)
                ),
                evaluation_cost=test_case.get(
                    "evaluationCost"
                ),
                metrics=metrics,
                trajectory=trajectory,
            )
        )

    return results