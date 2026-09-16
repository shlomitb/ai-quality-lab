## Procedure

1. Retrieve the relevant ticket using `get_ticket`.

2. Identify the repository from the ticket information.
   Use the ticket information rather than making assumptions.

3. Run the repository tests using `run_tests`.

4. If tests fail, carefully inspect the failure information.
   Identify the failing test, test file, failure message, and relevant
   source file when that information is available.

5. If the test failure identifies a relevant source file, use
   `read_file` to inspect that file before modifying it.

6. Use the information from the ticket, test failure, and source code
   to determine the likely cause.

   Do not repeatedly search for the same code using increasingly
   similar search terms.

   - If `run_tests` identifies a relevant source file, use `read_file`
     on that file directly.

   - Do not use `search_files` to locate a file when its path is already
     known from `run_tests` or another tool result.

   - Use `search_files` only when the relevant file cannot be identified
     from the available tool results.

7. Use `edit_file` to make the smallest appropriate code change.

8. After every successful code change, run `run_tests` again.

9. Do not report that the bug is fixed unless the post-change
   test run shows that the tests pass.

10. If the tests still fail, use the new failure information to
    continue investigating and make another appropriate change.