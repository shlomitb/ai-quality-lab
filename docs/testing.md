# Testing Guide

This project uses several different types of tests. Each type checks a different layer of the AI agent and its supporting code.

The goal is not to make every test check everything. Instead, the test suite separates deterministic code checks, agent behavior, end-to-end regression, and LLM-judge evaluation.

## Test Types

### 1. Deterministic tests

Deterministic tests do not make LLM calls.

They test the application's Python code, configuration, tools, skill routing, file handling, provider behavior, and other logic that should produce predictable results.

Examples include:

* Tool behavior and error handling
* Skill selection and tool authorization
* Prompt/configuration construction
* Provider message formatting
* File safety checks
* Shared-state fixtures

These tests should be fast and stable.

Run the complete deterministic suite with:

```powershell
python -m pytest tests -m "not llm" -q
```

This is the main test suite to run after making ordinary code changes.

---

### 2. LLM behavior tests

These tests make real LLM calls and test how the agent behaves in specific situations.

They are used for questions such as:

* Did the agent select the appropriate tool?
* Did it use tools in an appropriate order?
* Did it recover correctly from a tool result?
* Did it request additional tool access when needed?
* Did it produce an appropriate response?

Because they depend on a live LLM, these tests can be affected by:

* API availability
* rate limits such as 429 responses
* temporary service errors such as 503 responses
* model variability

They should therefore not be treated like ordinary deterministic unit tests.

LLM tests are marked with the `llm` pytest marker and require the project's LLM configuration.

---

### 3. DeepEval tests

DeepEval is used to evaluate higher-level agent behavior with metrics such as:

* `ToolCorrectnessMetric`
* `StepEfficiencyMetric`
* `TaskCompletionMetric`

These metrics answer different questions.

**Tool correctness**

> Did the agent choose appropriate tools for the task?

**Step efficiency**

> Did the agent avoid unnecessary steps and tool calls?

**Task completion**

> Did the agent actually accomplish the requested task?

A single agent run may therefore score differently on different metrics. For example, an agent can eventually complete a task while still taking an inefficient route.

#### Running DeepEval tests

Tests using DeepEval's `assert_test(golden=..., metrics=...)` must be run through the DeepEval test runner so that an active DeepEval trace is available.

For example:

```powershell
deepeval test run tests\deepeval\task_completion_deepeval.py
```

To run a specific test:

```powershell
deepeval test run tests\deepeval\task_completion_deepeval.py -k test_bug_fix_agent_task_completion
```

These tests make LLM calls and may fail because of temporary API problems even when the code and test are correct.

---

### 4. Golden agent regression tests

Golden tests are end-to-end regression tests for important user scenarios.

They ask:

> Can the complete agent accomplish this task and produce the expected outcome?

Golden tests should generally check the **outcome**, not require an exact tool sequence.

For example, a golden test might require that the final answer contains:

```text
passed
```

rather than requiring the exact sequence:

```text
get_ticket
run_tests
```

Exact tool behavior belongs in more focused LLM behavior tests.

Current golden tests are located under:

```text
tests/
└── golden/
    └── test_golden_agent_regression.py
```

Their test data is stored separately under:

```text
tests/
└── fixtures/
    └── golden_agent_cases.json
```

Run the golden tests with:

```powershell
python -m pytest tests\golden\test_golden_agent_regression.py -q --run-llm
```

For debugging a golden test and seeing the complete trajectory:

```powershell
python -m pytest tests\golden\test_golden_agent_regression.py -s -q --run-llm
```

The `-s` option displays temporary diagnostic output such as tool calls and tool results.

Once a golden scenario is stable, unnecessary diagnostic printing should be removed from the test.

---

### 5. Standalone LLM judge learning tests

The project also contains a separate learning exercise for an LLM-as-a-judge implementation.

This is different from testing the main agent.

The standalone judge takes a predefined AI response and asks the judge model to evaluate it according to defined criteria.

The learning code is under:

```text
learning/
└── standalone_llm_judge/
```

Its test data is kept with the learning material:

```text
learning/
├── data/
│   └── judge_test_cases.json
└── standalone_llm_judge/
    ├── evaluator.py
    └── judge_runner.py
```

The JSON file contains reference AI responses and their expected judge evaluations.

The data-validation test checks that the cases are correctly structured. It does **not** call the LLM.

Run the data-validation test with:

```powershell
python -m pytest tests\test_judge_evaluation_cases_data.py -q
```

Run the actual standalone judge cases with:

```powershell
python -m learning.standalone_llm_judge.judge_runner
```

This makes a real LLM call for each case.

`MAX_CASES` in `judge_runner.py` can be used to run only a subset of the cases while developing the judge.

---

## Test Data and Fixtures

Test data should be kept separate from application/runtime data.

For example:

```text
tests/
├── fixtures/
│   └── golden_agent_cases.json
```

contains test data for the agent's golden regression tests.

By contrast:

```text
learning/data/
└── judge_test_cases.json
```

belongs to the standalone judge learning exercise.

Fixtures that modify shared state or repository files should restore that state after each test.

For example:

* `reset_shared_state` restores in-memory test state such as `bug_fixed` and `orders`.
* `restore_login_file` restores `demo-app_fail/src/login.py` after a test that actually modifies the file.

Tests that only test error handling for `edit_file` do not need the file-restoration fixture when the operation cannot modify a file.

---

## Running Tests After Changes

A useful normal workflow is:

### After ordinary code changes

Run the deterministic suite:

```powershell
python -m pytest tests -m "not llm" -q
```

### After changing a golden scenario

Run the golden tests:

```powershell
python -m pytest tests\golden\test_golden_agent_regression.py -q --run-llm
```

### After changing DeepEval tests

Run the relevant file with the DeepEval runner:

```powershell
deepeval test run tests\deepeval\<test_file>.py
```

### After changing the standalone judge

Run the data test:

```powershell
python -m pytest tests\test_judge_evaluation_cases_data.py -q
```

Then run the actual judge:

```powershell
python -m learning.standalone_llm_judge.judge_runner
```

---

## Interpreting LLM Test Failures

A failed LLM test does not automatically mean the test is wrong or the code is wrong.

When an LLM test fails, first look at the agent trajectory:

```text
Tool Calls
Tool Results
Final Response
```

Then determine which layer failed.

Possible causes include:

* Incorrect skill selection
* Incorrect initial or requestable tool policy
* Poor prompt/context
* Unnecessary tool calls
* Invalid tool requests
* Failure to stop after completing the task
* Failure to complete the requested task
* Temporary API errors such as 429 or 503
* Normal LLM variability

The test should not be weakened simply to make a model run pass. A failing test may be revealing a real agent-quality problem.

---

## Keep Test Purposes Separate

Tests should have one primary purpose.

For example:

```text
ToolCorrectnessMetric
    → tool choice

StepEfficiencyMetric
    → efficiency

TaskCompletionMetric
    → successful completion

Golden regression
    → important end-to-end outcome

Deterministic tests
    → predictable application behavior

Standalone judge tests
    → judge/evaluator behavior
```

Avoid duplicating the same assertion across several test types unless the duplication is intentional.

---

## LLM Test Stability

Live LLM tests are inherently less deterministic than ordinary Python tests.

The project should therefore:

* Keep deterministic tests fast and stable.
* Use focused LLM scenarios rather than very long conversations.
* Avoid requiring one exact tool sequence unless the sequence itself is what the test is evaluating.
* Avoid unnecessary tool calls in agent workflows.
* Use explicit task wording so the expected behavior is clear.
* Keep golden assertions focused on important outcomes.
* Treat 429 and 503 errors as service/API issues unless the test reveals a reproducible application problem.

A successful test should mean more than "the model happened to do something that satisfied the assertion." The scenario and assertion should represent behavior that is actually desirable for the agent.

---

## Current Testing Layers

The overall testing architecture is:

```text
                    AI QUALITY LAB
                          │
        ┌─────────────────┼──────────────────┐
        │                 │                  │
   Deterministic      LLM behavior      Golden tests
       tests              tests          end-to-end
        │                 │                  │
        │          ┌──────┴──────┐           │
        │          │             │           │
        │      DeepEval       targeted       │
        │       metrics       behavior        │
        │          │             │            │
        └──────────┼─────────────┼────────────┘
                   │             │
             Application     Agent quality
                code          regressions

Separate learning project:
    standalone LLM judge
```

This separation makes it possible to tell **what failed and why**, rather than having one large collection of tests that all measure the same thing.
