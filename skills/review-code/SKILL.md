# Review Code

Use this procedure when a user asks to review, inspect, or assess source code.

## Procedure

1. Identify the repository and relevant file or files.

2. If the file path is already known, use `read_file` rather than searching
   for the file.

3. Once `read_file` has successfully returned the requested file, do not
   search for that file again and do not call `read_file` again unless
   additional information is required that was not included in the result.

4. If the file path is not known, use `search_files` to locate it.

5. Review the code for:
   - correctness and possible bugs
   - unclear or risky logic
   - unnecessary complexity
   - maintainability and readability issues

6. Do not modify the code unless the user explicitly asks for a fix.

7. Clearly distinguish confirmed problems from suggestions or concerns.

8. Do not run tests unless the user explicitly asks you to run or verify tests.

9. Clearly distinguish confirmed problems from suggestions or concerns.

## Constraints

- Use information returned by tools rather than making assumptions.
- Avoid repeated searches or reads for the same file or code.
- Once a tool has successfully returned the information needed for the
  current step, use that information rather than repeating the tool call.
- Do not modify tests or source files unless explicitly requested.