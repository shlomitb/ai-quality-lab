# Security

This document describes the security model and security controls implemented in the AI Quality Lab agent.

The project treats tool access as a security boundary. The agent may reason about tools and request additional capabilities, but the application—not the language model—decides whether a tool may actually execute.

---

## 1. Security Principles

The agent follows these basic security principles:

* The LLM does not determine its own permissions.
* A tool being registered with the application does not mean the current skill is authorized to use it.
* Initial permissions and requestable permissions are separate.
* Additional access must be authorized by application code before execution.
* Unknown or unlisted tools cannot be authorized through the access-request mechanism.
* Tool arguments are validated before sensitive filesystem operations.
* Tool results are treated as untrusted input and are not allowed to override application security rules.
* Security controls are enforced deterministically in application code rather than relying only on prompt instructions.

---

# 2. Tool Access Policy

Each skill has three categories of tool access:

### Initial tools

Initial tools are tools that the skill is authorized to use immediately.

When a skill is selected, these tools are placed in the skill's currently authorized tool list.

### Requestable tools

Requestable tools are tools that the skill is allowed to request if needed.

They are **not authorized initially**.

The agent must use the `request_tool_access` mechanism, and the application must check the skill policy before granting access.

A successful request adds the requested tool to the skill's currently authorized tools for that agent run.

### Unauthorized tools

Tools that are neither initial nor requestable for the selected skill are unauthorized.

They cannot be granted through `request_tool_access`.

---

# 3. Registered Tools vs Authorized Tools

The application may know about more tools than the selected skill is currently allowed to execute.

Conceptually:

```text
Registered tools
    = tools that exist in the application/runtime

Currently authorized tools
    = tools the selected skill is permitted to execute now

Requestable tools
    = additional tools this skill is allowed to request
```

This distinction is important.

A tool may exist in the runtime and still be denied to the current skill.

For example, `run_tests` may exist in the registered tool set while not being initially authorized for `review-code`.

The authorization check must therefore happen before the tool is executed.

---

# 4. Current Skill Policies

The current policy is defined by `TOOL_ACCESS_POLICY`.

## `investigate-bug`

### Initially authorized

```text
get_ticket
run_tests
read_file
edit_file
```

### Requestable

```text
get_repository
search_files
```

### Not authorized

Any tool not listed above.

---

## `review-code`

### Initially authorized

```text
search_files
read_file
```

### Requestable

```text
run_tests
```

### Not authorized

Any tool not listed above.

For example:

```text
edit_file
get_ticket
get_repository
```

are not authorized for `review-code` unless the policy is explicitly changed.

---

# 5. Authorization Flow

The intended access flow is:

```text
User request
    ↓
Skill selected
    ↓
Initial tools become authorized
    ↓
Agent works with authorized tools
    ↓
Agent determines another tool is needed
    ↓
request_tool_access(tool_name)
    ↓
Application checks TOOL_ACCESS_POLICY
    ↓
 ┌───────────────────────────────┐
 │ Is the tool requestable       │
 │ for this selected skill?      │
 └───────────────┬───────────────┘
                 │
          ┌──────┴──────┐
          │             │
         YES            NO
          │             │
          ↓             ↓
   Grant authorization  Deny request
          │
          ↓
 Add tool to currently
 authorized tools
          │
          ↓
 Agent may execute tool
```

The important security property is:

> A request is not authorization by itself. The application must authorize the requested tool before execution.

---

# 6. Enforcement at Tool Execution

The application performs an authorization check before executing a normal tool call.

Conceptually:

```python
if tool_call.name not in selected_skill.tools:
    deny_execution()
```

This means that even when a tool is physically present in the registered tool set, the call is rejected when the selected skill is not currently authorized to use it.

This creates two separate checks:

```text
Does the tool exist?
        ↓
Is the tool authorized for this skill?
        ↓
Execute
```

Both conditions must be satisfied.

---

# 7. Requestable Tool Security

A requestable tool follows a different path from an initial tool.

For example, `review-code` initially has:

```text
search_files
read_file
```

and may request:

```text
run_tests
```

At the start of the run:

```text
run_tests → not authorized
```

After a successful request:

```text
run_tests → authorized
```

The application must never treat a requestable tool as automatically authorized merely because it appears in the policy's `requestable_tools` list.

The requestable list defines **what may be requested**, not **what is currently authorized**.

---

# 8. Unknown and Unlisted Tools

An agent must not be able to create new capabilities simply by inventing a tool name.

For example, a request such as:

```text
request_tool_access("delete_database")
```

must not grant access unless that tool is explicitly requestable for the selected skill.

This protects against an LLM generating a plausible-sounding but unauthorized tool name.

---

# 9. Tool Permission Testing

Tool authorization is tested at two levels.

## Deterministic security tests

Deterministic tests verify the application enforcement directly.

Examples include:

* an unauthorized requestable tool is blocked before execution
* denied access does not grant the tool
* authorization for one tool does not grant another tool
* an unlisted tool cannot be authorize
