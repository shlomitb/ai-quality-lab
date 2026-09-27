import subprocess

from src.tools import run_tests


def test_run_tests_handles_timeout(monkeypatch):
    """
    An agent-triggered operation must have a bounded amount of time it is allowed to consume.
    """
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=kwargs.get("args", "pytest"),
            timeout=30,
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_tests("demo-app_fail")

    assert result["result"]["error"] == "Test execution timed out."