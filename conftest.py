import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-llm",
        action="store_true",
        default=False,
        help="run tests that require real LLM/API calls",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-llm"):
        return

    skip_llm = pytest.mark.skip(
        reason="LLM test skipped; use --run-llm to run it"
    )

    for item in items:
        if "llm" in item.keywords:

            item.add_marker(skip_llm)