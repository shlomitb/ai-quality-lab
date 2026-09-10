# AI Agent Testing Rules

## 1. Use the simplest test that proves the requirement

**Deterministic requirement → deterministic test**

Use normal Python/pytest assertions when the expected behavior is precise.

Examples:

```python
assert tool_name == "get_product_information"
assert order_id == "12345"
assert "49.99" not in response.text
```

Don't use an LLM judge for something that can be checked exactly.

---

## 2. Separate unit tests from LLM integration tests

**Unit test:**
Test the Python tool/function itself.

```text
tool
→ expected result
```

No Gemini/OpenAI call.

**LLM integration test:**
Run the real agent and let the LLM make the decision.

```text
real LLM
→ real tool
→ real result
→ real agent response
```

Then use deterministic assertions to check important requirements.

---

## 3. `@observe` records execution; it does not cause execution

```python
@observe(type="agent")
def my_agent():
```

means:

> Record this function's execution in the trace.

It does **not** make the function run.

The function runs because Python calls it.

Similarly:

```python
@observe(type="tool")
```

records a tool call as a span in the trace.

---

## 4. Trace vs. span

**Trace = the complete agent run**

**Span = one recorded operation inside the trace**

Example:

```text
TRACE
└── Agent
    ├── LLM call
    ├── Tool call
    ├── LLM call
    └── Tool call
```

Trajectory evaluation looks at the complete trace.

Component evaluation can look at individual spans/actions.

---

## 5. Tool call and tool result are different things

A Gemini trace may contain:

```text
FunctionCall
    ↓
FunctionResponse
```

That means:

```text
CALL
 ↓
RESULT
```

It does **not** mean the tool was called twice.

---

## 6. Agent trajectories may contain multiple valid paths

Don't automatically assume:

> More tool calls = bad.

Ask:

> Was each action justified by the task and the information available at that point?

Example:

```text
get_order_information
→ check_return_eligibility
→ get_return_policy
```

may be reasonable for explaining a return decision.

But:

```text
get_return_policy
→ get_product_information
→ get_return_policy
```

contains an obviously redundant call.

---

## 7. Use trajectory metrics for semantic questions

Use DeepEval when the question is difficult to express as an exact assertion.

Examples:

**TaskCompletionMetric**

> Did the agent accomplish the overall task?

**StepEfficiencyMetric**

> Was the trajectory efficient and free of unnecessary steps?

These evaluate the whole trajectory rather than one individual tool call.

---

## 8. Don't blindly trust an LLM judge

An evaluation score is itself an LLM judgment.

For example:

```text
Task Completion = 0.95
```

does not mean:

> "The agent is exactly 95% correct."

Interpret the score together with the evaluator's reason.

Validate evaluators against cases where you already know the expected outcome.

---

## 9. Evaluator validation is different from agent testing

**Agent test:**

> Is my agent behaving correctly?

**Evaluator validation:**

> Is my evaluator behaving sensibly?

For evaluator validation, use controlled cases where the expected quality is known.

Example:

```text
clearly successful
clearly partial
clearly failed
```

Then check whether the evaluator distinguishes them sensibly.

---

## 10. Tool design affects agent behavior

If a tool returns too little information, the agent may make unnecessary additional calls.

Example:

```text
eligible = False
reason = "Does not meet requirements."
```

may cause the agent to retrieve the policy separately.

A better tool result might include:

```text
eligible = False
reason = "Opened defective products can only be returned
within 14 days. This order is 20 days old."
```

Good tool outputs can reduce unnecessary agent steps.

---

## 11. Agent-quality improvement is an iterative loop

A useful workflow is:

```text
Observe
   ↓
Test
   ↓
Evaluate
   ↓
Find undesirable behavior
   ↓
Diagnose why
   ↓
Improve prompt/tool design
   ↓
Retest
   ↓
Verify improvement
```

Don't simply change the prompt until the score goes up.

First understand **why** the undesirable behavior happened.

---

## 12. Test failure handling and recovery separately

**Failure handling:**

```text
tool fails
→ agent does not hallucinate
→ truthful response
```

**Recovery:**

```text
tool fails
→ agent chooses appropriate fallback
→ fallback succeeds
→ task completed
```

These are different behaviors and should be tested separately.

---

## 13. Exact trajectory vs. acceptable trajectory

A deterministic test may require:

```text
Tool A
→ Tool B
```

But real agents can sometimes have several valid paths.

Use deterministic assertions for **hard requirements**.

Use trajectory evaluation when the question is:

> Was the overall path reasonable?

---

## 14. Avoid unnecessary expensive LLM test runs

Real LLM tests cost time, API requests, and sometimes money.

Use:

```powershell
pytest -v -k test_name
```

to run one specific test.

Use:

```powershell
pytest -v -s
```

when you need to see `print()` output.

Don't rerun a successful LLM test simply to reconfirm it unless there is a reason.

---

## 15. Keep experiments separate from permanent tests

A useful distinction is:

```text
tests/
    permanent regression tests

experiments/
    learning experiments
    evaluator calibration
    exploratory investigations
```

An experiment should not automatically become part of the permanent test suite.

Only keep it when it represents a useful ongoing regression check.

---

## 16. Think in evaluation layers

A useful mental model is:

```text
Final answer
    ↓
semantic correctness

Tool selection
    ↓
correct tool?

Arguments
    ↓
correct inputs?

Tool result
    ↓
correct result?

Trajectory
    ↓
successful?
efficient?

Failure/recovery
    ↓
safe?
robust?
```

Use the appropriate test for each layer rather than trying to test everything with one metric.
