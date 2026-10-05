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

        # Extract a concise agent trajectory from DeepEval's trace.
        trajectory = []

        trace = test_case.get("trace") or {}

        for agent_span in trace.get("agentSpans", []):

            # Current DeepEval format:
            # agentSpan -> toolsCalled -> execute_tool_call -> output.name
            for tool_call in agent_span.get("toolsCalled", []):
                output = tool_call.get("output") or {}
                tool_name = output.get("name")

                if not tool_name:
                    continue

                if tool_name == "request_tool_access":
                    requested_tool = (
                        tool_call
                        .get("inputParameters", {})
                        .get("tool_call", {})
                        .get("args", {})
                        .get("tool_name")
                    )

                    if requested_tool:
                        trajectory.append(
                            f"request_tool_access({requested_tool})"
                        )
                    else:
                        trajectory.append(tool_name)

                else:
                    trajectory.append(tool_name)

            # Fixture / simplified format:
            # agentSpan -> output -> tool_calls -> name
            if not agent_span.get("toolsCalled"):
                output = agent_span.get("output") or {}

                for tool_call in output.get("tool_calls", []):
                    tool_name = tool_call.get("name")

                    if not tool_name:
                        continue

                    if tool_name == "request_tool_access":
                        requested_tool = (
                            tool_call
                            .get("args", {})
                            .get("tool_name")
                        )

                        if requested_tool:
                            trajectory.append(
                                f"request_tool_access({requested_tool})"
                            )
                        else:
                            trajectory.append(tool_name)

                    else:
                        trajectory.append(tool_name)

        # Older/simplified DeepEval fixtures may store the trajectory
        # directly in the trace.
        if not trajectory:
            trajectory = trace.get("trajectory", [])

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