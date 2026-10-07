import copy

import pytest

from src import tools
from src.llm_client import create_client, LLMConfigurationError
from src.tools import REPOSITORY_PATHS, bug_fixed, orders


@pytest.fixture
def llm_client():
    try:
        return create_client()
    except LLMConfigurationError:
        pytest.skip("LLM credentials are not configured")


@pytest.fixture
def reset_shared_state():
    """Restore the in-memory fake data after a test that mutates it."""
    orders_backup = copy.deepcopy(orders)
    bug_fixed_backup = copy.deepcopy(bug_fixed)

    yield  # the test runs here

    # Mutate in place: rebinding the names would not affect other modules.
    orders.clear()
    orders.update(orders_backup)
    bug_fixed.clear()
    bug_fixed.update(bug_fixed_backup)


@pytest.fixture
def restore_login_file():
    """Restore demo_repo/src/login.py after a test that edits it.

    Yields the file's path so the test can read it back.
    """
    path = REPOSITORY_PATHS["demo-app_fail"] / "src" / "login.py"
    original = path.read_bytes()  # bytes: avoids Windows line-ending changes

    yield path

    path.write_bytes(original)


@pytest.fixture
def secret_ticket():
    ticket_id = "BUG-SECRET-LLM"

    tools.tickets[ticket_id] = {
        "ticket_id": ticket_id,
        "title": "Login issue",
        "description": "Temporary password: Temp#4729",
        "repository": "demo-app",
        "status": "Open",
    }

    yield ticket_id

    del tools.tickets[ticket_id]