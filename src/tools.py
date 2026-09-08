

from deepeval.tracing import observe

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
    return {
        "category": "physical",
        "name": product_name,
        "price": 49.99,
    }
