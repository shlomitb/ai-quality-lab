"""
Tests:
A timeout is actually configured.
A timeout is handled safely.
"""


import subprocess

from src import tools
from src.tools import run_tests


def test_run_tests_handles_timeout(monkeypatch):
    """
    An agent-triggered operation must have a bounded amount of time
    it is allowed to consume.
    """

    def fake_run(*args, **kwargs):
        assert kwargs["timeout"] == tools.RUN_TESTS_TIMEOUT

        raise subprocess.TimeoutExpired(
            cmd=kwargs.get("args", "pytest"),
            timeout=kwargs["timeout"],
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_tests("demo-app_fail")

    assert result["result"]["error"] == "Test execution timed out."