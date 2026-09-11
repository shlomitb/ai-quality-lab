# AI Agent Testing Rules

## 1. Use the simplest test that proves the requirement

**Deterministic requirement → deterministic test**

Use normal Python/pytest assertions when the expected behavior is precise.

Examples:


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


@observe(type="agent")
def my_agent():


means:

> Record this function's execution in the trace.

It does **not** make the function run.

The function runs because Python calls it.

Similarly:


@observe(type="tool")


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


# New Rules — Multi-Step Agents and State Validation

## 17. Test multi-step dependencies

In a real agent, a later tool call may depend on information returned by an earlier tool.

Example:

```text
get_order_information("12345")
        ↓
returns product, purchase date, opened, defective
        ↓
check_return_eligibility(...)
        ↓
returns eligible = False
```

Test not only that the tools were called, but that information from the first result was correctly used as arguments to the next tool.

---

## 18. Don't require an exact trajectory unless it is a hard requirement

An agent may have more than one valid way to complete a task.

Prefer:


assert tool_call_details[0] == expected_first_step
assert tool_call_details[1] == expected_second_step


when specific steps are required.

Avoid:


assert tool_call_details == [...]


unless the entire sequence is genuinely required.

Use trajectory evaluation when the question is:

> Was the overall path reasonable and efficient?

---

## 19. Efficiency is contextual

More tool calls do not automatically mean an inefficient agent.

The important question is:

> Was each action justified by the task and the information available at that point?

For example:

```text
get_order_information
→ check_return_eligibility
→ get_return_policy
```

may be reasonable for a task requiring an eligibility decision plus explanation.

But an unnecessary duplicate such as:

```text
get_return_policy
→ get_product_information
→ get_return_policy
```

is much easier to identify as redundant.

`StepEfficiencyMetric` evaluates the usefulness of steps in context rather than simply counting them.

---

## 20. Tool output affects agent efficiency

If a tool returns insufficient information, the agent may need additional tool calls.

Poor output:

```python
{
    "eligible": False,
    "reason": "Does not meet requirements."
}
```

Better output:

```python
{
    "eligible": False,
    "reason": (
        "Opened defective products can only be returned within "
        "14 days. This order is 20 days old."
    )
}
```

A well-designed tool result can allow the agent to finish without an unnecessary follow-up call.

Therefore, when an agent takes an inefficient path, investigate both:

```text
agent instructions
+
tool design / tool output
```

before changing the prompt.

---

## 21. Separate failure handling from recovery

Failure handling means:

```text
tool fails
→ agent does not hallucinate
→ agent gives a truthful response
```

Recovery means:

```text
tool fails
→ agent chooses an appropriate alternative
→ alternative succeeds
→ agent completes the task
```

Test these behaviors separately.

---

## 22. Verify actual state changes

Never rely only on the agent's final statement.

If the agent says:

> "Order 12345 has been updated."

verify the actual state:

assert orders["12345"]["status"] == "Reviewed"


The agent's response is evidence of what it believes happened.

The actual system state is evidence of what really happened.

---

## 23. State validation is different from response validation

Response validation asks:

> Did the agent say the correct thing?

State validation asks:

> Did the system actually end up in the correct state?

For a coding agent, examples of state validation include:

```text
file was actually modified
tests actually pass
ticket status actually changed
database record was actually updated
commit was actually created
```

State validation is often stronger than trusting the final response alone.

---

## 24. Combine deterministic tests with semantic evaluation

Use deterministic assertions for facts that can be known exactly:

```text
correct tool
correct arguments
correct state
required facts in final answer
```

Use DeepEval/LLM evaluation for broader questions:

```text
Was the task completed?
Was the trajectory efficient?
Was the recovery reasonable?
```

The strongest test strategy often combines both.

---

## 25. Evaluate the whole workflow, not just individual actions

For a multi-step agent, think in layers:

```text
Task
 ↓
Tool 1
 ↓
Result 1
 ↓
Agent interpretation
 ↓
Tool 2
 ↓
Result 2
 ↓
Agent interpretation
 ↓
State change
 ↓
Final answer
```

A good evaluation strategy checks important properties at multiple points in this chain rather than relying on a single final score.

---

## 26. Agent quality is an iterative loop

A useful workflow is:

```text
Observe
 ↓
Test
 ↓
Evaluate
 ↓
Identify undesirable behavior
 ↓
Diagnose the cause
 ↓
Improve tool/prompt/agent design
 ↓
Retest
 ↓
Verify the improvement
```

Do not change the agent simply to make an evaluation score higher. First understand why the behavior was considered undesirable.

---

## 27. An agent's claim is not proof

A useful rule for agent testing:

> **Trust the system state more than the agent's claim about the system state.**

Whenever possible, verify important side effects independently.

# New Rules — Failure Recovery and Multi-Step Workflows

## 28. A tool failure is not automatically an agent failure

A tool can fail and the agent can still have a successful trajectory.

Example:

```text
get_order_information
        ↓
ERROR
        ↓
search_order_database
        ↓
SUCCESS
```

Evaluate whether the agent responded appropriately to the failure and recovered when possible.

---

## 29. Test recovery separately from safe failure

When a tool fails, there are two important scenarios.

**Recovery is possible:**

```text
tool fails
→ appropriate fallback
→ fallback succeeds
→ continue task
```

**Recovery is not possible:**

```text
tool fails
→ fallback fails
→ agent stops safely
→ truthful response
→ no hallucination
```

Both behaviors should be tested.

---

## 30. Multi-step agents must carry information forward correctly

In a multi-step workflow, a later tool call may depend on information returned by an earlier tool.

Example:

```text
get_order_information("54321")
        ↓
product_name = Example Product
days_since_purchase = 10
opened = True
defective = True
        ↓
check_return_eligibility(...)
```

The test should verify that the information from the first step is correctly used to construct the next tool call.

---

## 31. Test the chain, not only individual tools

A tool can work perfectly in isolation while the agent still uses it incorrectly.

Test both:

```text
Unit test
→ Does the tool work?

Agent integration test
→ Does the agent use the tool correctly?

Trajectory evaluation
→ Does the complete workflow make sense?
```

---

## 32. Verify the actual outcome, not just the agent's claim

If an agent says:

> "The order was updated."

that is not proof.

Whenever possible, verify the actual state independently:


assert orders["12345"]["status"] == "Reviewed"

The agent's final response tells us what the agent believes happened.

The system state tells us what actually happened.

---

## 33. Tool output is part of agent design

When an agent makes an unnecessary additional tool call, investigate the tool output before assuming the agent is the problem.

For example:

```text
eligible = False
reason = "Does not meet requirements."
```

may force the agent to retrieve additional information.

A richer result:

```text
eligible = False
reason = "Opened defective products can only be returned
within 14 days. This order is 20 days old."
```

may allow the agent to complete the task directly.

Agent quality depends on:

```text
prompt/instructions
+
tool definitions
+
tool arguments
+
tool results
```

---

## 34. Efficiency depends on context

Do not define efficiency simply as "fewest tool calls."

The correct question is:

> Was each step justified by the task and the information available at that point?

A three-step trajectory can be efficient when all three steps are necessary.

A two-step trajectory can be inefficient if one step is redundant.

---

## 35. Deterministic tests and trajectory evaluation have different jobs

Use deterministic assertions for precise requirements:

```text
correct tool
correct arguments
required facts
actual state
required final information
```

Use trajectory evaluation for broader questions:

```text
Was the task completed?
Was the trajectory efficient?
Was the recovery reasonable?
```

The strongest agent tests often combine both.

---

## 36. Agent testing is an iterative improvement loop

A useful workflow is:

```text
Observe
   ↓
Test
   ↓
Evaluate
   ↓
Identify undesirable behavior
   ↓
Diagnose the cause
   ↓
Improve prompt/tool/agent design
   ↓
Retest
   ↓
Verify improvement
```

An evaluation score should be used to understand behavior, not simply to make the score go up.

---

## 37. Test the whole workflow from beginning to end

For a multi-step agent, think in terms of:

```text
User task
   ↓
Tool 1
   ↓
Result 1
   ↓
Agent decision
   ↓
Tool 2
   ↓
Result 2
   ↓
Agent decision
   ↓
State change / final outcome
   ↓
Final response
```

Important quality properties can exist at every stage.

---

## 38. A successful final answer is not sufficient evidence

An agent can produce a convincing final answer even when something went wrong earlier.

Therefore, evaluate:

```text
trajectory
+
tool results
+
final response
+
actual state
```

rather than relying only on the final text.

## 39. Verify information flow between agent steps

In a multi-step agent, a later tool call may depend on information returned by an earlier tool.

Test that the agent correctly carries information forward.

Example:

```text
User asks about BUG-123
        ↓
get_ticket("BUG-123")
        ↓
repository = "demo-app"
        ↓
get_repository("demo-app")
        ↓
language = Python
```

The test should verify both:

```text
✅ the correct first tool was called
✅ the information returned by the first tool was correctly used in the next tool's arguments
```

This tests the agent's ability to maintain and use context across a multi-step workflow.
