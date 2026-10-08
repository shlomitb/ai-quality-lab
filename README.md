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


## Security Testing

AI agents introduce security concerns that are different from traditional application testing.

This project includes tests for:

#### Prompt injection

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

TThe project collects results from multiple evaluation sources and combines
them into a structured quality report.

The reporting pipeline can include:

* Pytest results
* DeepEval metrics and evaluation results
* LLM-as-a-judge results
* agent trajectories
* historical quality reports
* comparison with a previous run
* regression and improvement detection

The report is designed to distinguish ordinary automated-test failures from
AI-quality evaluation findings.

The report can be generated with:

```powershell
python -m src.reporting.generate_quality_report
```

Generated reports are kept out of source control.

---

## Running the Tests

From the project root:

### Run tests that do not require a real LLM

```markdown id="r4k8n2"
> **Note:** `demo_repo/` contains an intentionally failing test. The
> `demo-app_fail` repository is used by agent investigation and code-repair
> scenarios, so its failure is expected. The deterministic `ai-quality-lab`
> test suite can be run independently with the `demo_repo` excluded.

```powershell
python -m pytest -q --ignore=demo_repo
```

### Run a specific test file

```powershell
python -m pytest path\to\test_file.py -q
```

### DeepEval tests

DeepEval tests require a configured LLM/API and may consume API quota.

```powershell
deepeval test run tests\deepeval
```

The tests marked `llm` are separated from the regular deterministic test suite
so that the two types of testing can be run independently. LLM tests require
a configured model/API and may be affected by model availability, rate limits,
or API quota.

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

The project is an ongoing learning and portfolio project.

The deterministic `ai-quality-lab` test suite currently contains **205 passing
tests**. The `demo_repo/` contains an intentionally failing test used by agent
investigation and code-repair scenarios.

LLM-based evaluations are kept separate because they depend on external model
availability, rate limits, and API quota.

The project intentionally combines:

**traditional software testing + AI evaluation + security testing + tracing
and execution analysis**

rather than treating AI quality as only an LLM scoring problem.

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