# AI Quality Lab

An experimental project for learning and building **AI agent quality, evaluation, testing, and security**.

The project started as a hands-on exploration of how to test AI systems beyond traditional software testing. It has evolved into a small AI-agent testing lab covering agent behavior, tool use, evaluation, security, tracing, and quality reporting.

The goal is to understand not only **how to use evaluation frameworks such as DeepEval**, but also the concepts behind them and how to build reliable tests for AI systems.

---

## What This Project Explores

The project focuses on several areas of AI quality:

* **AI agent testing** — evaluating whether an agent follows the required procedure and completes a task correctly.
* **LLM evaluation** — measuring whether an AI response satisfies expected behavior and criteria.
* **Tool-use and trajectory testing** — checking which tools an agent selects,
how it uses them, whether tool arguments are valid, and whether its sequence
of actions is appropriate and efficient.
* **Dynamic tool access** — testing whether an agent can request access to tools that are not initially available.
* **Security testing** — testing protections against prompt injection, unauthorized tool access, path traversal, sensitive-information leakage, and resource exhaustion.
* **Tracing and execution analysis** — capturing information about agent execution and tool-call trajectories for evaluation and debugging.
* **Quality reporting** — combining test results and evaluation results into a structured quality report.

---

## The AI Agent

The project contains a tool-using AI agent with different skills, including:

* `investigate-bug`
* `review-code`
* `customer-support`

Each skill defines the procedure the agent should follow and the tools it is initially allowed to use.

Some tools can be requested dynamically when they are needed. Tool access is
controlled by an explicit policy that distinguishes between tools available
initially and tools that may be requested later. Additional access must be
explicitly authorized rather than being left entirely to the model.

The agent can work with tools such as:

* reading files
* searching files
* running tests
* editing files
* retrieving demonstration ticket information
* accessing repository information when authorized

The project also records agent execution information for evaluation and tracing.

---

## Evaluation Approach

The project uses several complementary approaches rather than relying on a single score.

### Pytest

Traditional Python tests verify deterministic application behavior, including:

* tool behavior
* skill selection
* tool authorization
* argument validation
* security protections
* provider behavior
* report generation and serialization

The majority of the test suite does not require an external LLM.

### Real LLM integration tests

A separate set of Pytest tests runs the agent against a real LLM. These tests
verify agent behavior such as tool selection, tool arguments, multi-step
workflows, failure recovery, dynamic tool access, task boundaries, and
security-related behavior.

These tests are marked `llm` and are kept separate from the deterministic
suite because they depend on external model availability, rate limits, and API
quota.

### DeepEval

DeepEval is used to evaluate AI-agent behavior with specialized evaluation
metrics and agent traces.

Examples include testing:

* task completion
* tool selection
* tool arguments
* tool permissions
* step efficiency
* agent traces

The DeepEval tests include both deterministic metric-level tests and
LLM-backed agent evaluations. Tests that require a real LLM depend on model
availability, rate limits, and API quota.

### LLM-as-a-Judge

Before adopting DeepEval, I built a standalone LLM-as-a-judge implementation to understand the underlying concepts.

This earlier implementation:

1. sends an AI response to a judge model,
2. asks the model to evaluate it against a policy and criteria,
3. requests structured JSON output,
4. validates the result with Pydantic,
5. returns the structured evaluation result for further analysis.

This implementation is intentionally preserved as a learning example. It is
separate from the current agent evaluation architecture, where DeepEval is used
for specialized agent and trajectory evaluation.

This earlier implementation is preserved under:

```text
learning/standalone_llm_judge/
```

It is kept as a learning example rather than being part of the current main evaluation architecture.

---

### Golden and regression testing

The project includes golden evaluation cases with expected outcomes for
agent behavior and judge evaluations.

These cases can be used to detect regressions when the agent, prompts, tools,
policies, or evaluation logic change. The project also includes comparison of
quality reports from different runs to identify changes in evaluation results.



## What This Project Demonstrates

This project explores how QA engineers can test AI agents whose decisions are not fully predictable.

It demonstrates a layered testing approach:

- **Deterministic tests** for application rules, permissions, and security controls.
- **Mocked agent tests** for controlled failure scenarios and evidence-based behavior.
- **Live LLM tests** for model-driven tool selection and multi-step workflows.
- **LLM-based evaluations** for assessing agent behavior beyond exact-match assertions.
- **Regression testing** for detecting changes in agent behavior and evaluation results.

The central principle is that an agent's final answer is not sufficient evidence of correctness. Tests should also examine the actions taken, the tools used, the evidence obtained, and whether the actions were authorized.

---

## Security Testing

AI agents introduce security concerns that are different from traditional application testing.

This project includes tests for:

### Prompt injection

Tests whether malicious instructions contained in untrusted data can influence
agent behavior, and whether the application's authorization layer prevents
unauthorized actions even if such an instruction is followed.

### Tool authorization

Tests that the agent can execute only tools authorized for the selected skill.
This includes least-privilege controls and dynamic tool access, where additional
tools must be explicitly requested and authorized before they can be used.

### Tool argument validation

Tests that tools validate potentially unsafe arguments before execution. This
includes path-traversal attempts that could access or modify files outside the
authorized repository, while still allowing normalized paths that remain
inside the repository.

### Sensitive information

Tests that sensitive information is removed or redacted before it reaches the
agent or appears in the final response. This includes explicit sensitive fields
as well as secrets embedded in otherwise unclassified fields.

### Resource limits

Tests protections such as bounded test-execution timeouts so that an
agent-triggered operation cannot consume an unbounded amount of time.

---

## Project Structure

```text
.
├── data/                       # Test and evaluation data
├── demo_repo/                  # Small repositories used by the agent
├── docs/                       # Project documentation and testing rules
├── learning/
│   └── standalone_llm_judge/   # Earlier LLM-as-a-judge learning implementation
├── src/
│   ├── agent.py               # Agent and execution flow
│   ├── skills.py              # Skills and tool-access policy
│   ├── tools.py               # Agent tools
│   ├── tool_catalog.py        # Tool definitions and descriptions
│   ├── providers/              # LLM provider abstraction
│   └── reporting/              # Quality-report generation
└── tests/
    ├── security/               # Agent security tests
    ├── reporting/              # Quality-report tests
    ├── deepeval/               # DeepEval-based evaluations
    ├── golden/                 # Golden/regression tests
    ├── fixtures/               # Shared evaluation and test data
    └── learning/               # Tests for learning implementations
```

---

## Quality Reporting

The project combines results from multiple testing and evaluation sources into a structured Markdown quality report.

The report can include:

- **Pytest results:** passed, failed, skipped, and error counts
- **DeepEval results:** agent-evaluation outcomes, metric scores, thresholds, and reasons
- **LLM-as-a-judge results:** whether the judge correctly identified the expected outcome
- **Agent trajectories:** the sequence of tool calls and actions taken by the agent
- **Run information:** a run ID and timestamp
- **Historical comparison:** changes between the current run and a previous run, including reported regressions and improvements

The report distinguishes ordinary automated-test failures from AI-quality evaluation findings. It also helps distinguish an agent failing an evaluation from an evaluator correctly identifying that failure.

A successfully generated report does not mean that the agent passed every test or evaluation. The report presents the results and findings from the available evaluation sources so that failures can be investigated and distinguished from failures of the evaluation mechanisms themselves.

Generate the report after producing the required input reports:

```powershell
python -m src.reporting.generate_quality_report
```

Generated reports are kept out of source control.

---

## Running the Tests

Run commands from the project root.

### Deterministic and non-LLM tests

The `demo_repo/` directory contains an intentionally failing test used by agent investigation and code-repair scenarios. It is excluded from the main project test run. The exclusion prevents the demo repository's expected failure from being counted as a failure of the main project's own tests.
```powershell
python -m pytest -q --ignore=demo_repo
```

### Generating the Quality Report

The quality report combines Pytest results with the latest available DeepEval and LLM-as-a-judge results.

Generate the report using the existing result files, without running Pytest:

```powershell
python -m src.reporting.generate_quality_report
```

To run the deterministic Pytest suite first, refresh the JUnit XML results, and then generate the report:

```powershell
python -m src.reporting.generate_quality_report --run-pytest
```

The `--run-pytest` option runs the main test suite with `demo_repo` excluded. Test failures are included in the report rather than preventing report generation.

Neither command automatically runs DeepEval or the LLM-as-a-judge tests. Those results are loaded from their existing report files and may therefore reflect an earlier evaluation run.


### Run a specific test file

```powershell
python -m pytest tests/test_agent_config.py -q
```

### Live LLM tests

Tests that call a real LLM depend on model availability, API credentials, rate limits, and quota. Run them separately from the deterministic suite to control cost and variability.

```powershell
python -m pytest -m llm -v
```

### DeepEval evaluations

DeepEval evaluations may also require an LLM and consume API quota. Run the specific evaluation you want to examine:

```powershell
deepeval test run tests/deepeval/dynamic_tool_access_deepeval.py
```

Check the project's pytest configuration and actual test markers to confirm that each command selects the intended tests.

---

## Learning Progression

One purpose of this repository is to document the progression from basic AI evaluation concepts toward more complete AI-agent quality testing.

The project began with a simple standalone LLM-as-a-judge implementation and
then expanded into a broader AI-agent quality lab:

```text
LLM-as-a-Judge
      ↓
Deterministic and mocked agent testing
      ↓
Real LLM agent testing
      ↓
Tool-use and trajectory evaluation
      ↓
Dynamic tool access and authorization
      ↓
Security testing
      ↓
Regression and golden testing
      ↓
Quality reporting
```

Keeping the earlier implementation in the `learning/` directory makes it possible to compare the concepts and understand what evaluation frameworks provide.

---

## Current Focus

The current focus is **AI agent quality, reliability, and security**.

Areas covered include:

* evaluating agent behavior and task completion
* evaluating tool selection, arguments, results, and trajectories
* testing failure recovery and dynamic tool access
* testing authorization, least privilege, and security boundaries
* evaluating execution efficiency
* detecting quality and security regressions
* generating structured quality reports from multiple evaluation sources

---

## Current Status

The project is an ongoing learning and portfolio project focused on AI agent quality, reliability, and security.

### Deterministic test suite

- **Last verified:** October 11, 2026
- **Command:** `python -m pytest -q --ignore=demo_repo`
- **Result:** 206 passed, 0 failed, 26 skipped

The `demo_repo/` directory contains an intentionally failing test used by agent investigation and code-repair scenarios. It is excluded from the main project test run.

### LLM-based evaluations

Live LLM tests and LLM-backed evaluations are maintained separately from the deterministic suite because they depend on model availability, API credentials, rate limits, and quota.

- **Last verified:** [date, or "Not run in this status update"]
- **Evaluations run:** [list the specific test files or evaluation groups]
- **Result:** [brief summary of the actual results]

The project combines traditional software testing, AI evaluation, security testing, and execution analysis rather than treating AI quality as only an LLM scoring problem.

---

## Why This Project?

Traditional software tests can tell us whether code behaves correctly for known inputs.

AI systems introduce additional questions:

* Did the model choose the right tool?
* Did it follow the required procedure?
* Did it use the correct arguments?
* Did it access information it should not have?
* Did it complete the task?
* Can an adversarial input change its behavior?
* Can we detect regressions when the model or prompt changes?

This project explores those questions in a practical, testable way. The focus
is not simply on whether an AI system produces the right final answer, but also
on how the agent behaves, what actions it takes, whether those actions are
authorized and efficient, and whether the system can detect quality and
security regressions.