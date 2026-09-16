

from deepeval.tracing import observe
from pathlib import Path
import subprocess
import sys

orders = {
    "12345": {
        "order_id": "12345",
        "product_name": "Example Product",
        "days_since_purchase": 20,
        "opened": True,
        "defective": True,
        "status": "Open",
    },
    "54321": {
        "order_id": "54321",
        "product_name": "Example Product",
        "days_since_purchase": 10,
        "opened": True,
        "defective": True,
        "status": "Open",
    },
}


tickets = {
    "BUG-123": {
        "ticket_id": "BUG-123",
        "title": "Login button does not work",
        "description": "Clicking the login button does nothing.",
        "repository": "demo-app",
        "status": "Open",
    },
    "BUG-456": {
        "ticket_id": "BUG-456",
        "title": "Login function returns False for valid credentials",
        # "description": (
        #     "The login test is failing because valid username and "
        #     "password combinations are not accepted."
        # ),
        "description": (
            "The login function incorrectly rejects valid credentials. "
            "The failing test involves the login button."
        ),
        "repository": "demo-app_fail",
        "status": "Open",
    },
}

repositories = {
    "demo-app": {
        "name": "demo-app",
        "language": "Python",
        "path": "C:/Projects/demo-app",
        "default_branch": "main",
    }
}

bug_fixed = {
    "BUG-456": False
}

files = {
    "demo-app": {
        "src/login.py": """
        def login(username, password):
            if username and password:
                return True
            return False
        """,
                "tests/test_login.py": """
        def test_login():
            assert login("alice", "password") is True
        """,
                "README.md": """
        # Demo App
        
        Simple login application.
        """,
    },
    "demo-app_fail": {
        "src/login.py": """
        def login(username, password):
            if username and password:
                return True
            return False
        """,
        "tests/test_login.py": """
        def test_login_button():
            assert login("alice", "password") is True
        """,
     },
}


@observe(type="tool")
def get_return_policy():
    return """
    Customers may return unopened products within 30 days.
    
    Opened products may be returned within 14 days
    only if they are defective.
    
    Digital products cannot be returned.
    
    Refunds are issued to the original payment method.
    """


@observe(type="tool")
def get_product_information(product_name: str) -> dict:
    if product_name in {"Unavailable Product", "Unknown Product"}:
        return {
            "result": {
                "error": "Product information service is temporarily unavailable."
            }
        }

    return {
        "result": {
            "category": "physical",
            "name": product_name,
            "price": 49.99,
        }
    }


@observe(type="tool")
def search_product_catalog(product_name: str) -> dict:
    """
    For testing with specific product names.
    Records this function call in the trace
    A real fallback tool with controlled data
    @observe(type="tool") means: When this function runs, DeepEval records it as a tool span.
    """

    products = {
        "Example Product": {
            "category": "physical",
            "name": "Example Product",
            "price": 49.99,
        },
        "Unavailable Product": {
            "category": "physical",
            "name": "Unavailable Product",
            "price": 49.99,
        },
    }

    product = products.get(product_name)


    if product is None:
        return {
            "result": {
                "error": "Product not found in catalog."
            }
        }

    if product_name == "Unknown Product":
        return {
            "result": {
                "error": "Product not found in catalog."
            }
        }

    return {
        "result": product
    }


@observe(type="tool")
def get_order_information(order_id: str) -> dict:
    if order_id == "54321":
        return {
            "result": {
                "error": "Order information service is temporarily unavailable."
            }
        }

    order = orders.get(order_id)

    if order is None:
        return {
            "result": {
                "error": "Order not found."
            }
        }

    return {
        "result": order
    }


@observe(type="tool")
def update_order_status(order_id: str, status: str) -> dict:
    order = orders.get(order_id)

    if order is None:
        return {
            "result": {
                "error": "Order not found."
            }
        }

    order["status"] = status

    return {
        "result": {
            "order_id": order_id,
            "status": status,
        }
    }


@observe(type="tool")
def check_return_eligibility(
    product_name: str,
    days_since_purchase: int,
    opened: bool,
    defective: bool,
) -> dict:
    if days_since_purchase <= 30 and not opened:
        return {
            "result": {
                "eligible": True,
                "reason": "Unopened products can be returned within 30 days.",
            }
        }

    if days_since_purchase <= 14 and opened and defective:
        return {
            "result": {
                "eligible": True,
                "reason": "Opened defective products can be returned within 14 days.",
            }
        }

    return {
        "result": {
            "eligible": False,
            "reason": (
                "Opened defective products can only be returned within "
                "14 days. This order is 20 days old."
            ),
        }
    }

@observe(type="tool")
def search_order_database(order_id: str) -> dict:
    order = orders.get(order_id)

    if order is None:
        return {
            "result": {
                "error": "Order not found in database."
            }
        }

    return {
        "result": order
    }


@observe(type="tool")
def get_ticket(ticket_id: str) -> dict:
    ticket = tickets.get(ticket_id)

    if ticket is None:
        return {
            "result": {
                "error": "Ticket not found."
            }
        }

    return {
        "result": ticket
    }


@observe(type="tool")
def get_repository(repository_name: str) -> dict:
    repository = repositories.get(repository_name)

    if repository is None:
        return {
            "result": {
                "error": "Repository not found."
            }
        }

    return {
        "result": repository
    }


@observe(type="tool")
def search_files(repository_name: str, search_term: str) -> dict:
    repository_files = files.get(repository_name)

    if repository_files is None:
        return {
            "result": {
                "error": "Repository not found."
            }
        }

    matches = []

    for file_path, content in repository_files.items():
        if search_term.lower() in content.lower():
            matches.append({
                "file_path": file_path,
                "content": content,
            })

    if not matches:
        return {
            "result": {
                "matches": []
            }
        }

    return {
        "result": {
            "matches": matches
        }
    }


@observe(type="tool")
def run_tests(repository_name: str) -> dict:
    if repository_name == "demo-app":
        return {
            "result": {
                "status": "passed",
                "tests_run": 1,
                "tests_failed": 0,
            }
        }

    if repository_name == "demo-app_fail":
        repo_path = Path("demo_repo")
        #runs: python -m pytest -q .
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                ".",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return {
                "result": {
                    "status": "passed",
                    "output": result.stdout,
                }
            }

        return {
            "result": {
                "status": "failed",
                "output": result.stdout,
                "error_output": result.stderr,
                "source_file": "src/login.py",
            }
        }

    return {
        "result": {
            "error": "Repository not found."
        }
    }



@observe(type="tool")
def apply_fix(ticket_id: str) -> dict:
    if ticket_id == "BUG-456":
        bug_fixed["BUG-456"] = True

        return {
            "result": {
                "status": "fixed",
                "ticket_id": ticket_id,
                "message": "The login button issue was fixed.",
            }
        }

    return {
        "result": {
            "error": "No supported fix is available for this ticket."
        }
    }


@observe(type="tool")
def edit_file(
        repository_name: str,
        file_path: str,
        new_content: str,
    ) -> dict:

    repository_paths = {
        "demo-app": Path("demo_repo"),
        "demo-app_fail": Path("demo_repo"),
    }

    repo_path = repository_paths.get(repository_name)

    if repo_path is None:
        return {
            "result": {
                "error": "Repository not found."
            }
        }

    full_path = repo_path / file_path

    if not full_path.exists():
        return {
            "result": {
                "error": "File not found."
            }
        }

    full_path.write_text(new_content)

    return {
        "result": {
            "status": "updated",
            "repository_name": repository_name,
            "file_path": file_path,

        }
    }



@observe(type="tool")
def read_file(repository_name: str, file_path: str) -> dict:
    repository_paths = {
        "demo-app": Path("demo_repo"),
        "demo-app_fail": Path("demo_repo"),
    }

    repo_path = repository_paths.get(repository_name)

    if repo_path is None:
        return {
            "result": {
                "error": "Repository not found."
            }
        }

    full_path = repo_path / file_path

    if not full_path.exists():
        return {
            "result": {
                "error": "File not found."
            }
        }

    return {
        "result": {
            "repository_name": repository_name,
            "file_path": file_path,
            "content": full_path.read_text(),
        }
    }

