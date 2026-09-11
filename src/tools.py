

from deepeval.tracing import observe


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
    }
}

repositories = {
    "demo-app": {
        "name": "demo-app",
        "language": "Python",
        "path": "C:/Projects/demo-app",
        "default_branch": "main",
    }
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