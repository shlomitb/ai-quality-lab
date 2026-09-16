# Review Code

Use this procedure when a user asks to review, inspect, or assess source code.

## Procedure

1. Identify the repository and relevant file or files.

2. If the relevant file path is already known, use `read_file`
   rather than searching for the file.

3. If the file path is not known, use `search_files` to locate it.

4. Read the relevant source code before making any conclusions.

5. Review the code for:
   - correctness and possible bugs
   - unclear or risky logic
   - unnecessary complexity
   - maintainability and readability issues

6. Do not modify the code unless the user explicitly asks for a fix.

7. Clearly distinguish confirmed problems from suggestions or concerns.

## Constraints

- Use information returned by tools rather than making assumptions.
- Avoid repeated searches for the same file or code.
- Do not modify tests or source files unless explicitly requested.