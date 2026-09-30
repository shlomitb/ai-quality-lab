# AI Quality Lab

An experimental project for learning and building **AI agent quality, evaluation, testing, and security**.

The project started as a hands-on exploration of how to test AI systems beyond traditional software testing. It has evolved into a small AI-agent testing lab covering agent behavior, tool use, evaluation, security, tracing, and quality reporting.

The goal is to understand not only **how to use evaluation frameworks such as DeepEval**, but also the concepts behind them and how to build reliable tests for AI systems.

---

## What This Project Explores

The project focuses on several areas of AI quality:

* **AI agent testing** — evaluating whether an agent follows the required procedure and completes a task correctly.
* **LLM evaluation** — measuring whether an AI response satisfies expected behavior and criteria.
* **Tool-use testing** — checking which tools an agent selects, how it uses them, and whether tool arguments are valid.
* **Dynamic tool access** — testing whether an agent can request access to tools that are not initially available.
* **Security testing** — testing protections against prompt injection, unauthorized tool access, path traversal, sensitive-information leakage, and resource exhaustion.
* **Tracing and observability** — capturing information about agent execution and tool calls.
* **Quality reporting** — combining test results and evaluation results into a structured quality report.

---

## The AI Agent

The project contains a tool-using AI agent with different skills, including:

* `investigate-bug`
* `review-code`

Each skill defines the procedure the agent should follow and the tools it is initially allowed to use.

Some tools can be requested dynamically when they are needed. Tool access is controlled by an explicit policy rather than being left entirely to the model.

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

### DeepEval

DeepEval is used for evaluation of AI-agent behavior and LLM-based metrics.

Examples include testing:

* task completion
* tool selection
* tool arguments
* tool permissions
* step efficiency
* agent traces

Some DeepEval tests require a real LLM call and therefore depend on API availability and quota.

### LLM-as-a-Judge

Before adopting DeepEval, I built a standalone LLM-as-a-judge implementation to understand the underlying concepts.

That implementation:

1. sends an AI response to a judge model,
2. asks the model to evaluate it against a policy and criteria,
3. requests structured JSON output,
4. validates the result with Pydantic,
5. compares the result against expected behavior.

This earlier implementation is preserved under:

```text
learning/standalone_llm_judge/
```

It is kept as a learning example rather than being part of the current main evaluation architecture.

---

## Security Testing

AI agents introduce security concerns that are different from traditional application testing.

This project includes tests for:

### Prompt injection

Tests whether malicious instructions contained in data can cause the agent to perform actions that are not authorized by its current skill.

### Tool authorization

Tests that the agent cannot execute tools that are outside the tools authorized for the selected skill.

### Tool argument validation

Tests unsafe arguments such as path-traversal attempts that could access files outside the allowed repository.

### Sensitive information

Tests that sensitive information is removed or redacted before it reaches inappropriate parts of the system.

### Resource limits

Tests protections such as timeouts for test execution so that an agent cannot cause an unbounded operation.

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
    ├── reporting/              # Reporting tests
    ├── deepeval/               # DeepEval-based evaluations
    └── learning/               # Tests for learning implementations
```

---

## Quality Reporting

The project collects results from multiple sources and combines them into a quality report.

The current reporting pipeline can include:

* Pytest results
* DeepEval results
* judge results
* historical quality reports
* comparison with a previous run

The report can be generated with:

```powershell
python -m src.reporting.generate_quality_report
```

Generated reports are kept out of source control.

---

## Running the Tests

From the project root:

### Run tests that do not require a real LLM

```powershell
python -m pytest tests -m "not llm" -q
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

The tests marked `llm` are separated from the regular deterministic test suite so that the two types of testing can be run independently.

---

## Learning Progression

One purpose of this repository is to document the progression from basic AI evaluation concepts toward more complete AI-agent quality testing.

The project began with a simple standalone LLM judge using structured Pydantic output.

It then evolved toward:

```text
LLM-as-a-Judge
      ↓
DeepEval metrics
      ↓
Agent trace evaluation
      ↓
Tool-use evaluation
      ↓
Security testing
      ↓
Quality reporting
```

Keeping the earlier implementation in the `learning/` directory makes it possible to compare the concepts and understand what evaluation frameworks provide.

---

## Current Focus

The current focus is **AI agent quality and reliability**.

Areas being explored include:

* evaluating agent behavior
* evaluating tool selection and arguments
* testing dynamic tool access
* improving security boundaries
* tracing agent execution
* building reusable evaluation techniques
* understanding how AI quality measurements can be applied to real agent systems

---

## Current Status

The project is an ongoing learning and portfolio project.

The deterministic test suite currently contains more than 150 passing tests. LLM-based evaluations are kept separate because they depend on external model availability and API limits.

The project intentionally combines:

**traditional software testing + AI evaluation + security testing + observability**

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

This project is an attempt to explore those questions in a practical, testable way.
