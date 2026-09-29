# Test Running Guide – AI Quality Lab

This document is a reference for running and reviewing the project's tests.

## 1. Test organization

The project currently has three separate categories of tests.

### A. Deterministic / non-LLM tests

These tests do not intentionally make real LLM/API calls.

Run:

```powershell
python -m pytest tests -m "not llm" -q
```

Current verified result:

```text
136 passed, 23 deselected
```

The 23 deselected tests are the tests marked with:

```python
@pytest.mark.llm
```

This group includes unit, security, reporting, skill, tool, and mock-based tests.

---

### B. Ordinary real-LLM tests

These are normal pytest tests that use a real LLM/API and are marked:

```python
@pytest.mark.llm
```

Check which tests belong to this group without running them:

```powershell
python -m pytest tests -m llm --collect-only -q
```

Current collection:

```text
23 tests
```

Run them with:

```powershell
python -m pytest tests -m llm -q
```

Because these tests use a real LLM, they may be affected by API quota limits or temporary API errors.

---

### C. DeepEval tests

These tests are in:

```text
tests/deepeval/
```

Their filenames end in:

```text
*_deepeval.py
```

They are intentionally NOT discovered by ordinary pytest.

Run them with DeepEval:

```powershell
deepeval test run tests\deepeval
```

To run one file:

```powershell
deepeval test run tests\deepeval\step_efficiency_deepeval.py
```

To run one specific test:

```powershell
deepeval test run tests\deepeval\step_efficiency_deepeval.py -k test_login_verification_step_efficiency -v -s
```

---

# 2. What the pytest options mean

## `-m`

`-m` filters tests by pytest marker.

For this project:

```powershell
-m "not llm"
```

means:

> Run tests that are NOT marked `llm`.

```powershell
-m llm
```

means:

> Run only tests marked `llm`.

The marker is defined in `pytest.ini`:

```ini
[pytest]
markers =
    llm: test requires a real LLM/API call
```

---

## `-q`

`-q` means **quiet**.

It reduces the amount of pytest output.

Useful when the main thing you want is the final result:

```powershell
python -m pytest tests -m "not llm" -q
```

Typical ending:

```text
136 passed, 23 deselected
```

---

## `-v`

`-v` means **verbose**.

It shows more detail, including individual test names.

Useful when you are checking which tests ran or debugging a failure:

```powershell
python -m pytest tests -m "not llm" -v
```

---

## `-s`

`-s` tells pytest not to capture standard output.

This is useful when a test contains:

```python
print(...)
```

For example, your DeepEval tests temporarily print:

```python
print("\nAGENT TOOL CALLS:")
print(response.tool_calls)

print("\nFINAL RESPONSE:")
print(response.final_text)
```

To see those prints:

```powershell
deepeval test run tests\deepeval\step_efficiency_deepeval.py -v -s
```

---

# 3. Useful collection commands

Collection means:

> Check which tests pytest sees, without actually running them.

### All ordinary pytest tests

```powershell
python -m pytest tests --collect-only -q
```

### Only non-LLM tests

```powershell
python -m pytest tests -m "not llm" --collect-only -q
```

### Only ordinary LLM tests

```powershell
python -m pytest tests -m llm --collect-only -q
```

### DeepEval tests

Because the DeepEval files are excluded from ordinary pytest discovery, use DeepEval to run them:

```powershell
deepeval test run tests\deepeval
```

---

# 4. Recommended workflow

When Gemini/API quota is available:

## Step 1 – Check deterministic tests

```powershell
python -m pytest tests -m "not llm" -q
```

All of these should pass before relying on the LLM-based results.

## Step 2 – Run ordinary LLM tests

```powershell
python -m pytest tests -m llm -q
```

Because these use a real API, run them when quota is available.

## Step 3 – Run DeepEval tests

Run the DeepEval files one file at a time while validating them:

```powershell
deepeval test run tests\deepeval\step_efficiency_deepeval.py -v -s
```

Then:

```powershell
deepeval test run tests\deepeval\tool_selection_deepeval.py -v -s
```

and continue with the other DeepEval files.

Running one file at a time makes it easier to understand failures and reduces unnecessary LLM calls.

## Step 4 – Run the full DeepEval directory

After the individual files have been validated:

```powershell
deepeval test run tests\deepeval
```

## Step 5 – Generate the quality report

After the relevant tests have completed:

```powershell
python -m src.reporting.generate_quality_report
```

---

# 5. Important difference: pytest vs DeepEval

Some DeepEval tests use:

```python
assert_test(
    golden=golden,
    metrics=[metric],
)
```

These tests depend on the active DeepEval trace.

Therefore, run those tests with:

```powershell
deepeval test run ...
```

rather than:

```powershell
python -m pytest ...
```

Otherwise you can see an error such as:

```text
DeepEvalError:
No active trace found for this test.
```

Ordinary pytest is still useful for test collection.

---

# 6. How to interpret failures

A test failure does not automatically mean the test is bad.

## Example: Step Efficiency

A test can fail because the agent actually behaved inefficiently.

Example:

```text
Step Efficiency = 0.25
```

with a reason such as repeated unnecessary `run_tests` calls.

That can be a valuable finding.

The correct response is not necessarily to lower the threshold to make the test pass.

---

## API / infrastructure failure

Examples:

```text
429 RESOURCE_EXHAUSTED
```

or:

```text
503 Service Unavailable
```

These indicate an API/infrastructure problem rather than necessarily a problem with the test.

Do not change the test based only on a 429 or 503.

---

# 7. Current DeepEval coverage

The current DeepEval directory contains:

```text
tests/deepeval/
├── dynamic_tool_access_deepeval.py
├── helpers.py
├── real_code_task_completion_deepeval.py
├── step_efficiency_deepeval.py
├── task_completion_deepeval.py
├── tool_arguments_deepeval.py
├── tool_permission_deepeval.py
├── tool_selection_deepeval.py
└── __init__.py
```

The main quality dimensions are:

| File | Main question |
|---|---|
| `task_completion_deepeval.py` | Did the agent accomplish the requested task? |
| `step_efficiency_deepeval.py` | Did the agent avoid unnecessary steps? |
| `tool_selection_deepeval.py` | Did the agent select appropriate tools? |
| `tool_arguments_deepeval.py` | Were the tool arguments correct? |
| `tool_permission_deepeval.py` | Did the agent use only permitted tools? |
| `dynamic_tool_access_deepeval.py` | Can the agent complete a task requiring additional tool access? |
| `real_code_task_completion_deepeval.py` | Did the agent complete a task against real code/files? |

---

# 8. Current verified status

## Deterministic suite

```text
136 passed
23 deselected
```

Status: PASS

## Ordinary LLM suite

23 tests are correctly marked and isolated.

Status: Collection verified; full run should be done when API quota is available.

## DeepEval suite

15 tests are currently collected in the DeepEval directory.

Status: Individual validation in progress.

---

# 9. Temporary debugging output

During DeepEval test validation, it is useful to keep:

```python
print("\nAGENT TOOL CALLS:")
print(response.tool_calls)

print("\nFINAL RESPONSE:")
print(response.final_text)
```

Run with:

```powershell
-v -s
```

After the tests are stable, these debugging prints can be removed or reduced.

---

# 10. Quick reference

### Deterministic tests

```powershell
python -m pytest tests -m "not llm" -q
```

### Ordinary LLM tests

```powershell
python -m pytest tests -m llm -q
```

### DeepEval – all

```powershell
deepeval test run tests\deepeval
```

### DeepEval – one file

```powershell
deepeval test run tests\deepeval\step_efficiency_deepeval.py -v -s
```

### DeepEval – one test

```powershell
deepeval test run tests\deepeval\step_efficiency_deepeval.py -k test_login_verification_step_efficiency -v -s
```

### Generate the report

```powershell
python -m src.reporting.generate_quality_report
```
