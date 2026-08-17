
def get_return_policy():
    return """
    Customers may return unopened products within 30 days.
    
    Opened products may be returned within 14 days
    only if they are defective.
    
    Digital products cannot be returned.
    
    Refunds are issued to the original payment method.
    """


def get_product_information():
    return {
        "category": "physical",
        "name": "Example Product",
        "price": 49.99,
    }
