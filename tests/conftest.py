import copy

import pytest

from src.tools import REPOSITORY_PATHS, bug_fixed, orders


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