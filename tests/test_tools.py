from src.tools import (
    get_product_information,
    search_product_catalog,
    get_order_information,
    check_return_eligibility,
    )


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


def test_get_order_info_for_known_order():
    result = get_order_information("12345")

    assert result == {
        "result": {
            "order_id": "12345",
            "product_name": "Example Product",
            "days_since_purchase": 20,
            "opened": True,
            "defective": True,
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
