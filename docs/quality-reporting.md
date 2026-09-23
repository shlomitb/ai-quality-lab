# AI Quality Reporting

## 1. Purpose

The AI Quality Reporting system brings together results from different types of testing and evaluation into one normalized quality report.

The goal is not only to show whether tests passed or failed, but also to provide a broader view of AI-agent quality, including:

* traditional Python test results
* DeepEval behavioral evaluation
* agent tool trajectories
* evaluation scores and reasons
* changes between runs
* detected regressions and improvements

The reporting system separates **collecting test results**, **normalizing them**, **comparing runs**, and **presenting the results**.

This makes the reporting layer easier to extend later with additional quality signals such as security, performance, RAG evaluation, or observability data.

---

## 2. Reporting Architecture

The reporting flow is:

```text
                ┌─────────────────────┐
                │   Pytest XML        │
                │   JUnit report      │
                └──────────┬──────────┘
                           │
                           ↓
                  load_pytest_summary()
                           │
                           │
                ┌──────────┴──────────┐
                │                     │
                │    QualityReport    │
                │                     │
                └──────────┬──────────┘
                           │
                           │
                ┌──────────┴──────────┐
                │                     │
                ↓                     ↓
        history JSON             Markdown
                │                 report
                │
                ↓
       previous QualityReport
                │
                │
                ↓
    compare_quality_reports()
                │
                ↓
   QualityReportComparison
                │
                └──────────────→ Markdown
                                  report
```

DeepEval follows a similar path:

```text
DeepEval JSON
      ↓
load_deepeval_results()
      ↓
DeepEvalTestResult
      ↓
QualityReport
```

The important design principle is that **Markdown is a presentation format**. The normalized `QualityReport` JSON is used as the persistent representation for historical comparison.

---

## 3. Input Artifacts

The reporting system currently consumes two raw test artifacts.

### Pytest JUnit XML

Pytest can generate a JUnit XML report:

```powershell
pytest -v --junitxml=reports/pytest/junit.xml
```

The reporting code reads this XML and extracts a `PytestSummary` containing:

* total tests
* passed tests
* failed tests
* skipped tests
* errors
* total duration

The raw XML remains available in:

```text
reports/pytest/junit.xml
```

The parser is implemented in:

```text
src/reporting/pytest_report.py
```

The parser converts the XML into the normalized:

```python
PytestSummary
```

object.

### DeepEval JSON

The AI-agent evaluation is run using DeepEval:

```powershell
deepeval test run tests/deepeval/test_dynamic_escalation_deepeval.py -- --run-llm
```

The `-- --run-llm` portion is important because the project normally skips real LLM tests unless `--run-llm` is supplied.

DeepEval produces a timestamped JSON result under:

```text
reports/deepeval/
```

For example:

```text
reports/deepeval/
└── test_run_20260923_143831.json
```

The reporting system reads this JSON and extracts information such as:

* test name
* overall success
* duration
* evaluation cost
* DeepEval metric scores
* thresholds
* evaluation model
* evaluation reasons
* agent trajectory

The parser is implemented in:

```text
src/reporting/deepeval_report.py
```

---

## 4. QualityReport

The two input sources are converted into a common data model.

The central object is:

```python
QualityReport
```

It contains:

```python
@dataclass
class QualityReport:
    run_id: str
    timestamp: str

    pytest: PytestSummary | None = None
    deepeval: list[DeepEvalTestResult] = field(default_factory=list)

    security_results: dict[str, bool] = field(default_factory=dict)
    performance: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    comparison: QualityReportComparison | None = None
```

This gives the project one consistent structure for quality data from multiple sources.

### DeepEval data

A `QualityReport` can contain one or more:

```python
DeepEvalTestResult
```

Each result can contain multiple:

```python
DeepEvalMetricResult
```

For example:

```text
test_dynamic_escalation_agent

Task Completion
    score: 1.00
    threshold: 0.80
    status: PASS

Step Efficiency
    score: 1.00
    threshold: 0.80
    status: PASS
```

The agent trajectory is also preserved, for example:

```text
search_files
read_file
read_file
request_tool_escalation(run_tests)
run_tests
```

This is useful because behavioral evaluation is not limited to the final answer. The sequence of actions taken by the agent is also part of the quality signal.

---

## 5. Report Generation

The report generator coordinates the complete process.

The main module is:

```text
src/reporting/generate_quality_report.py
```

It performs the following steps:

1. Find the most recent DeepEval JSON result.
2. Re
