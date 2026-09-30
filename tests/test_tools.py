from pathlib import Path

import pytest

from src.tools import (
    REPOSITORY_PATHS,
    get_product_information,
    search_product_catalog,
    get_order_information,
    check_return_eligibility,
    orders,
    update_order_status,
    search_order_database,
    get_ticket,
    get_repository,
    search_files,
    run_tests,
    bug_fixed,
    apply_fix,
    edit_file,
    read_file,
)

# run with: pytest -v tests/test_tools.py
# Shared fixtures (reset_shared_state, restore_login_file) live in conftest.py


def test_get_product_information_returns_product():
    result = get_product_information("Example Product")

    assert result == {
        "result": {
            "category": "physical",
            "name": "Example Product",
            "price": 49.99,
        }
    }


def test_get_product_information_returns_error_for_unavailable_product():
    result = get_product_information("Unavailable Product")

    assert result == {
        "result": {
            "error": "Product information service is temporarily unavailable."
        }
    }


def test_search_product_catalog_finds_unavailable_product():
    result = search_product_catalog("Unavailable Product")

    assert result == {
        "result": {
            "category": "physical",
            "name": "Unavailable Product",
            "price": 49.99,
        }
    }


def test_search_product_catalog_fails_for_unknown_product():
    result = search_product_catalog("Unknown Product")

    assert result == {
        "result": {
            "error": "Product not found in catalog."
        }
    }


def test_get_order_info_for_known_order() -> None:
    result = get_order_information("12345")

    assert result == {
        "result": {
            "order_id": "12345",
            "product_name": "Example Product",
            "days_since_purchase": 20,
            "opened": True,
            "defective": True,
            "status": "Open",
        }
    }


def test_get_order_information_returns_error_for_unknown_order():
    result = get_order_information("99999")

    assert result == {
        "result": {
            "error": "Order not found."
        }
    }


def test_check_return_eligibility_for_opened_defective_product():
    result = check_return_eligibility(
        product_name="Example Product",
        days_since_purchase=20,
        opened=True,
        defective=True,
    )

    assert result == {
        "result": {
            "eligible": False,
            "reason": (
                "Opened defective products can only be returned within "
                "14 days. This order is 20 days old."
            ),
        }
    }


def test_check_return_eligibility_for_unopened_product():
    result = check_return_eligibility(
        product_name="Example Product",
        days_since_purchase=20,
        opened=False,
        defective=False,
    )

    assert result == {
        "result": {
            "eligible": True,
            "reason": "Unopened products can be returned within 30 days.",
        }
    }


def test_check_return_eligibility_for_opened_defective_product_within_14_days():
    result = check_return_eligibility(
        product_name="Example Product",
        days_since_purchase=10,
        opened=True,
        defective=True,
    )

    assert result == {
        "result": {
            "eligible": True,
            "reason": (
                "Opened defective products can be returned within 14 days."
            ),
        }
    }


def test_update_order_status(reset_shared_state):
    result = update_order_status("12345", "Reviewed")

    assert result == {
        "result": {
            "order_id": "12345",
            "status": "Reviewed",
        }
    }

    assert orders["12345"]["status"] == "Reviewed"


def test_get_order_information_fails_for_unavailable_order():
    result = get_order_information("54321")

    assert result == {
        "result": {
            "error": "Order information service is temporarily unavailable."
        }
    }


def test_search_order_database_finds_order():
    result = search_order_database("54321")

    assert result == {
        "result": {
            "order_id": "54321",
            "product_name": "Example Product",
            "days_since_purchase": 10,
            "opened": True,
            "defective": True,
            "status": "Open",
        }
    }


def test_get_ticket_for_known_ticket():
    result = get_ticket("BUG-123")

    assert result == {
        "result": {
            "ticket_id": "BUG-123",
            "title": "Login button does not work",
            "description": "Clicking the login button does nothing.",
            "repository": "demo-app",
            "status": "Open",
        }
    }


def test_get_ticket_for_unknown_ticket():
    result = get_ticket("BUG-999")

    assert result == {
        "result": {
            "error": "Ticket not found."
        }
    }


def test_get_repository_for_known_repository():
    result = get_repository("demo-app")["result"]

    assert result["name"] == "demo-app"
    assert result["language"] == "Python"
    assert result["default_branch"] == "main"
    # The path is machine-specific, so check it against the real location
    # instead of a hardcoded string.
    assert Path(result["path"]) == REPOSITORY_PATHS["demo-app"]
    assert Path(result["path"]).is_dir()


def test_get_repository_for_unknown_repository():
    result = get_repository("unknown-repo")

    assert result == {
        "result": {
            "error": "Repository not found."
        }
    }


def test_search_files_finds_matching_files():
    result = search_files("demo-app", "login")

    assert len(result["result"]["matches"]) == 3

    file_paths = {
        match["file_path"]
        for match in result["result"]["matches"]
    }

    assert "src/login.py" in file_paths
    assert "tests/test_login.py" in file_paths
    assert "README.md" in file_paths


def test_search_files_returns_empty_matches_when_nothing_found():
    result = search_files("demo-app", "database")

    assert result == {
        "result": {
            "matches": []
        }
    }


def test_search_files_returns_error_for_unknown_repository():
    result = search_files("unknown-repo", "login")

    assert result == {
        "result": {
            "error": "Repository not found."
        }
    }


def test_run_tests_for_known_repository():
    result = run_tests("demo-app")

    assert result == {
        "result": {
            "status": "passed",
            "tests_run": 1,
            "tests_failed": 0,
        }
    }


def test_run_tests_for_unknown_repository():
    result = run_tests("unknown-repo")

    assert result == {
        "result": {
            "error": "Repository not found."
        }
    }


def test_get_ticket_for_bug_456():
    result = get_ticket("BUG-456")

    assert result == {
        "result": {
            "ticket_id": "BUG-456",
            "title": "Login function returns False for valid credentials",
            "description": (
                "The login function incorrectly rejects valid credentials. "
                "The failing test involves the login button."
            ),
            "repository": "demo-app_fail",
            "status": "Open",
        }
    }


def test_apply_fix_for_bug_456(reset_shared_state):
    result = apply_fix("BUG-456")

    assert result == {
        "result": {
            "status": "fixed",
            "ticket_id": "BUG-456",
            "message": "The login button issue was fixed.",
        }
    }

    assert bug_fixed["BUG-456"] is True


def test_edit_file(restore_login_file):
    new_content = """def login(username, password):
    if username and password:
        return True
    return False
    """

    result = edit_file(
        repository_name="demo-app_fail",
        file_path="src/login.py",
        new_content=new_content,
    )

    assert result == {
        "result": {
            "status": "updated",
            "repository_name": "demo-app_fail",
            "file_path": "src/login.py",
        }
    }

    assert restore_login_file.read_text() == new_content


def test_run_tests_expect_failure():
    result = run_tests("demo-app_fail")

    assert result["result"]["status"] == "failed"
    assert "test_login_button" in result["result"]["output"]
    assert result["result"]["source_file"] == "src/login.py"


def test_read_file():
    result = read_file(
        repository_name="demo-app_fail",
        file_path="src/login.py",
    )

    assert result["result"]["repository_name"] == "demo-app_fail"
    assert result["result"]["file_path"] == "src/login.py"
    assert "def login" in result["result"]["content"]


# --- read_file / edit_file: error handling and security -------------------

TRAVERSAL_PATHS = [
    "../secret.txt",
    "../../etc/passwd",
    "src/../../outside.txt",
    "/etc/passwd",
]


def test_read_file_unknown_repository():
    result = read_file("unknown-repo", "src/login.py")

    assert result == {"result": {"error": "Repository not found."}}


def test_read_file_missing_file():
    result = read_file("demo-app_fail", "src/does_not_exist.py")

    assert result == {"result": {"error": "File not found."}}


@pytest.mark.parametrize("bad_path", TRAVERSAL_PATHS)
def test_read_file_blocks_path_traversal(bad_path):
    result = read_file("demo-app_fail", bad_path)

    assert result == {"result": {"error": "Invalid file path."}}


def test_edit_file_unknown_repository():
    result = edit_file("unknown-repo", "src/login.py", "x = 1")

    assert result == {"result": {"error": "Repository not found."}}


def test_edit_file_missing_file_is_not_created():
    result = edit_file("demo-app_fail", "src/new_file.py", "x = 1")
    new_file = REPOSITORY_PATHS["demo-app_fail"] / "src" / "new_file.py"

    assert result == {"result": {"error": "File not found."}}
    assert not new_file.exists()


@pytest.mark.parametrize("bad_path", TRAVERSAL_PATHS)
def test_edit_file_blocks_path_traversal(bad_path):
    result = edit_file("demo-app_fail", bad_path, "pwned")

    assert result == {"result": {"error": "Invalid file path."}}


def test_edit_file_traversal_does_not_write_outside_repository():
    outside = REPOSITORY_PATHS["demo-app_fail"].parent / "pwned.txt"

    try:
        edit_file("demo-app_fail", "../pwned.txt", "pwned")
        assert not outside.exists()
    finally:
        outside.unlink(missing_ok=True)


@pytest.mark.parametrize("empty_content", ["", "   ", "\n"])
def test_edit_file_rejects_empty_content(restore_login_file, empty_content):
    original = restore_login_file.read_text()

    result = edit_file("demo-app_fail", "src/login.py", empty_content)

    assert "error" in result["result"]
    assert restore_login_file.read_text() == original
