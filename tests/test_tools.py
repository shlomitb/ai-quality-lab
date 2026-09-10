from src.tools import get_product_information, search_product_catalog


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