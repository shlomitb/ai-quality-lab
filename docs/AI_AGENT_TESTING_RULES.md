# AI Agent Testing Rules

## 1. Use the simplest test that proves the requirement

**Deterministic requirement → deterministic test**

Use normal Python/pytest assertions when the expected behavior is precise.

Examples:


assert tool_name == "get_product_information"
assert order_id == "12345"
assert "49.99" not in response.final_text
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

## 40. Use deterministic checks for exact outcomes

If the expected result is a specific, known fact, verify it directly rather than relying only on an LLM evaluator.

For example:

clear
assert "python" in response.final_text.lower()
```

This directly verifies the agent answered "Python."

A DeepEval result such as:

```text
Task Completion = 1.0
```

provides a broader semantic judgment, but does not by itself prove the exact fact.

Use both when appropriate:

```text
Deterministic assertion
→ verifies the exact requirement

DeepEval
→ evaluates the broader quality of the trajectory
```

This combination provides stronger evidence than either approach alone.


## 41. Evaluate behavior against the task, not a fixed workflow

The correct agent trajectory depends on what the user asked for.

For example:

```text
"Run the tests and report failures."
→ get_ticket
→ run_tests
→ report result
```

But:

```text
"Investigate and fix the failing test."
→ get_ticket
→ run_tests
→ inspect relevant code
→ make a change
→ run_tests again
→ verify the fix
```

Do not assume that every task should produce the same sequence of tool calls.

Evaluate whether the actions taken were appropriate for the specific task.


## 42. Successful does not always mean efficient

An agent can successfully complete a task while taking an imperfect or unnecessary intermediate step.

For example:

```text
run_tests
→ failure
→ search_files("login button")
→ no results
→ search_files("login")
→ useful result
→ fix
→ tests pass
```

The task can still be fully successful, even though the first search was unproductive.

Therefore evaluate both:

```text
Task Completion
→ Did the agent ultimately succeed?

Step Efficiency
→ Did the agent avoid unnecessary or unproductive actions?
```

Do not treat every imperfect step as a complete agent failure. Consider whether the agent recovered appropriately.


## 43. Diagnose the cause of an agent failure before changing the test

When an agent test fails, do not immediately weaken the assertion.

First inspect:

```text
agent trajectory
tool arguments
tool results
runtime errors
final response
actual system state
```

Ask whether the failure was caused by:

```text
agent behavior
prompt/instructions
tool design
tool output
test design
runtime limitations
```

Fix the underlying cause whenever possible.

---

## 44. Tool contracts must be explicit

Tools that operate on repository or file resources should include enough context to identify the target unambiguously.

For example:


edit_file(
    repository_name="demo-app_fail",
    file_path="src/login.py",
    new_content="..."
)


is safer than:


edit_file(
    file_path="src/login.py",
    new_content="..."
)


The tool should validate the resource and return a clear error when it cannot find it.

---

## 45. Give the agent enough information to make the next decision

Tool results are part of the agent's working environment.

A failure result should contain useful information such as:

```text
failing test
test file
source file, when known
failure message
```

Poor tool output can cause unnecessary additional tool calls.

---

## 46. Require verification after side effects

When an agent changes code or system state:

```text
action
→ verify
```

For example:

```text
edit_file
→ run_tests
```

Do not allow the agent to report success merely because the edit tool returned successfully.

Whenever possible, verify the resulting state independently.

---

## 47. Don't test an exact implementation when the requirement is behavioral

A coding agent may solve the same problem in several valid ways.

Do not write a test such as:


assert file_contents == my_preferred_solution


unless the exact implementation is part of the requirement.

Prefer testing:

```text
correct behavior
tests pass
correct file changed
required outcome achieved


---

## 48. Agent investigation may contain imperfect steps

An agent may make an unsuccessful but reasonable investigative attempt.

For example:

```text
search_files("login button")
→ no result

search_files("login")
→ useful result
```

This does not necessarily mean the agent failed.

Distinguish:

```text
task failure
vs.
inefficient or imperfect intermediate behavior
```

Task completion and step efficiency measure different qualities.

---

## 49. Runtime limits are part of agent reliability

An agent can fail because it reaches a runtime/tool-call limit before completing its task.

For example:

```text
many exploratory tool calls
→ maximum automatic calls reached
→ no edit
→ no final response
```

This is different from a tool implementation error or a reasoning error.

When evaluating an agent, consider runtime constraints as part of the system being tested.

## 50. Agent quality includes resource efficiency

A successful agent is not necessarily an efficient production agent.

Consider:

```text
task completion
+
correctness
+
trajectory quality
+
resource usage
```

Additional tool calls, large tool outputs, long prompts, and repeated context can increase token usage and cost.

When diagnosing an inefficient agent, consider:

```text
unnecessary tool calls
large or unnecessary tool outputs
repeated searches
repeated context
unnecessarily long prompts
model choice
```

The goal is not to minimize tokens at all costs.

The goal is to minimize **unnecessary work while preserving correctness and reliability**.

A more expensive step can be justified when it reduces errors, improves reliability, or is necessary to complete the task.


## 51. Use progressive disclosure for large agent capabilities

When an agent has many capabilities, avoid putting all detailed instructions into the context on every request.

A progressive-disclosure design can use:

```text
Short capability/skill descriptions
        ↓
Agent decides what is relevant
        ↓
Load detailed instructions only when needed
```

This can reduce unnecessary context and token usage.

A skill is typically a reusable procedure or workflow, while a tool is a callable capability.

For example:

```text
Skill:
"Investigate a software bug."

Possible tools used by that skill:
get_ticket
run_tests
read_file
edit_file
```

The skill describes the procedure; the tools perform the individual actions.

The goal is not to minimize context at all costs. Detailed instructions should be loaded when they improve reliability or are needed to perform the task correctly.


## 52. Evaluate the whole agent system, not just the LLM

When an agent behaves poorly, the problem may not be the model itself.

Investigate all layers:

```text
prompt / instructions
+
tool definitions
+
tool inputs
+
tool outputs
+
agent decisions
+
runtime environment
+
evaluation/test design
```

For example, repeated searching may be caused by:

```text
unclear instructions
insufficient tool output
missing tool capability
ambiguous file paths
an unrealistic test environment
```

Before changing the model or weakening a test, identify which layer caused the behavior.

Improving the tools and environment can sometimes produce a larger improvement in agent behavior than adding more prompt instructions.

## 53. Separate provider-specific code from provider-neutral code

When supporting multiple LLM providers, keep provider-specific API structures inside the provider implementation.

For example:

```text
GeminiProvider
→ can know Gemini's response format

OpenAIProvider
→ can know OpenAI's response format

AgentResponse
→ common format used by the agent and general tests
```

General agent code and tests should use the provider-neutral interface rather than accessing provider-specific response structures directly.

This makes it possible to run the same behavioral tests against different providers.

---

## 54. Use regression tests when refactoring agent architecture

When changing the internal architecture of an agent, preserve existing behavior with regression tests.

For example:

```text
Before refactor:
agent → Gemini → tools

After refactor:
agent → provider interface → GeminiProvider → AgentResponse → tools
```

A previously passing LLM test can verify that the refactor did not unintentionally change agent behavior.

---

## 55. Separate repository rules, skills, and tools

Keep different kinds of instructions in the appropriate layer:

```text
AGENTS.md
→ repository-specific rules and constraints

SKILL.md
→ procedure for performing a particular type of task

Tool
→ action the agent can actually perform

Main agent prompt
→ general agent behavior and tool descriptions
```

Do not duplicate detailed task procedures across all of these layers unless there is a specific reason.

---

## 56. Skills should support progressive disclosure

When an agent has many capabilities, use short skill descriptions for discovery and load detailed instructions only when a skill is relevant.

Conceptually:

```text
short skill description
        ↓
agent identifies relevant capability
        ↓
load detailed SKILL.md
        ↓
perform procedure using tools
```

This can reduce unnecessary context while keeping detailed instructions available when needed.

Evaluate this architecture based on both reliability and resource usage rather than assuming that moving instructions into Skills automatically improves the agent.

---

## 57. Test architectural boundaries, not just individual functions

When introducing abstractions such as providers, verify that each layer has the responsibility intended for it.

For example:

```text
GeminiProvider
→ handles Gemini-specific response parsing

AgentResponse
→ represents the common response structure

agent.py
→ uses the common structure
```

A good test suite should help detect when provider-specific implementation details leak into provider-neutral application code.


## 58. Make one targeted change when improving agent efficiency

When an evaluation identifies a specific unnecessary or inefficient agent action:

1. Identify the specific behavior causing the inefficiency.
2. Make one targeted change to the relevant prompt, Skill, tool, or tool result.
3. Rerun the same task.
4. Compare the new agent trajectory with the previous one.

Do not add multiple new instructions at once when a single targeted change can test the hypothesis.

For example:

```text
Before:
run_tests
→ search_files("login")
→ read_file("src/login.py")

Change:
Explicitly instruct the agent not to use search_files when
the source file is already known.

After:
run_tests
→ read_file("src/login.py")
```

The goal is to determine whether the targeted change actually improves agent behavior, rather than simply making the prompt longer.

## 59. Test the agent at multiple layers

Use different types of tests for different responsibilities:

```text
Unit test
→ Tests one function or small piece of logic in isolation.
→ Example: select_skill() returns "investigate-bug" for a matching request.

Mock test
→ Tests how multiple parts of the agent connect, while replacing
  external or expensive dependencies with controlled fake objects.
→ Example: answer_customer_with_trace() passes the selected Skill's
  tools into the LLM configuration.

LLM integration test
→ Tests the real agent with a real model and real tool execution.
→ Example: the agent investigates BUG-456, edits the source code,
  and verifies the fix with tests.

DeepEval evaluation
→ Evaluates the quality of the agent's behavior or output using
  metrics such as task completion, correctness, or step efficiency.
→ Example: DeepEval evaluates whether the BUG-456 task was actually
  completed and whether the agent used unnecessary steps in its
  trajectory.
```

A useful way to think about the layers is:

```text
Unit test
→ Does this piece of code work?

Mock test
→ Do these pieces of the agent connect correctly?

LLM integration test
→ Does the real agent work with the real model and tools?

DeepEval
→ How good was the agent's behavior?
```

A failure at one layer does not necessarily indicate a failure at another layer.

Use the lowest-cost test that can reliably verify the behavior being tested, and use LLM integration tests and DeepEval evaluations when correctness depends on the real model, real tool interaction, or qualitative agent behavior.


## DeepEval: Behavioral and Trajectory Evaluation

DeepEval is used in this project to evaluate the **behavior of the complete AI agent**, not just individual functions or the final text response.

### What DeepEval adds

The project uses two DeepEval trajectory metrics:

* **Task Completion** — Did the agent accomplish the requested task?
* **Step Efficiency** — Did the agent complete the task without unnecessary or redundant steps?

These metrics evaluate the agent's **complete ordered trajectory**, including LLM calls, tool calls, and intermediate actions. DeepEval requires tracing in order to evaluate this trajectory.

### Example: Dynamic Tool Escalation

The dynamic-escalation test asks the agent to review the intentionally broken `demo-app_fail` repository and validate its conclusion using the repository's verification mechanism.

The expected trajectory is approximately:

```text
search_files
    ↓
read_file
    ↓
read_file
    ↓
request_tool_escalation("run_tests")
    ↓
run_tests
    ↓
final response
```

The escalation request is handled inside `execute_tool_call`, so the DeepEval trace displays that span as `execute_tool_call` rather than as a separate nested `request_tool_escalation` tool span.

### Why this is different from pytest tests

The deterministic pytest tests verify that the **escalation mechanism itself is correct**:

* authorized tools can be requested and added
* unauthorized tools are rejected
* the authorized tool becomes available on the next agent turn

The real LLM integration test verifies that a real model can actually use this mechanism during a real agent run.

DeepEval then evaluates the resulting **behavior and trajectory**:

```text
Unit tests
    → Does the individual code work?

Mock tests
    → Do the components work together?

Real LLM integration tests
    → Does the agent work with the real model and tools?

DeepEval trajectory evaluation
    → Did the agent complete the task effectively and efficiently?
```

### Inspecting a DeepEval run

The pytest output normally reports only whether the test passed or failed. DeepEval stores the evaluation trace separately.

After running the test, the trace can be inspected with:

```bash
deepeval inspect
```

The inspection view shows:

* the agent execution tree
* LLM spans
* tool spans
* the order of actions
* metric scores
* the LLM judge's reason for each metric score

For example:

```text
Task Completion: 1.00 / 0.80   PASS
Step Efficiency: 1.00 / 0.80   PASS
```

This makes it possible to investigate not only **whether** an evaluation passed, but also **how the agent behaved during the run**.

### Important limitation

DeepEval's trajectory metrics are LLM-as-a-judge evaluations. Their scores and explanations can therefore vary somewhat between runs.

For this reason, deterministic security and correctness requirements remain pytest assertions, while DeepEval is used for higher-level behavioral evaluation.

### Current DeepEval test

The dynamic-escalation evaluation is implemented in:

```text
tests/deepeval/test_dynamic_escalation_deepeval.py
```

It uses:

```text
TaskCompletionMetric
StepEfficiencyMetric
```

with a configured threshold of `0.8`.
