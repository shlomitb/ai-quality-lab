import pytest

from src.agent import (answer_customer_with_trace,
                       get_tool_calls,
                       get_tool_call_details,
                       get_tool_result_details)

from src.llm_client import create_client


#run with  --run-llm  at the end:
# pytest -v --run-llm tests/test_agent_tools_with_llm.py --run-llm


@pytest.mark.llm
def test_agent_calls_return_policy_tool():
    """Verify that the agent selects the return-policy tool."""
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="Can I return an opened product after 20 days if defective?"
    )

    tool_calls = get_tool_calls(response)

    print(tool_calls)

    assert tool_calls == ["get_return_policy"]


@pytest.mark.llm
def test_agent_selects_product_information_tool():
    """Verify that the agent selects the product-information tool."""
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Example Product?"
    )

    tool_calls = get_tool_calls(response)

    assert tool_calls == ["get_product_information"]


@pytest.mark.llm
def test_agent_passes_correct_product_name():
    """Verify that the agent passes the correct product name to the tool."""
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Example Product?"
    )

    tool_call_details = get_tool_call_details(response)

    assert tool_call_details == [
        {
            "name": "get_product_information",
            "args": {
                "product_name": "Example Product"
            }
        }
    ]


@pytest.mark.llm
def test_agent_receives_expected_product_information():
    """Verify that the expected product information appears in the tool result."""
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Example Product?"
    )

    tool_results = get_tool_result_details(response)

    assert tool_results == [
        {
            "name": "get_product_information",
            "response": {
                "result": {
                    "category": "physical",
                    "name": "Example Product",
                    "price": 49.99
                }
            }
        }
    ]


@pytest.mark.llm
def test_agent_handles_product_information_failure():
    """
    An LLM integration test.
    The LLM responded with the expected error, and it did not hallucinate a price
    :return:
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Unavailable Product?",
    )

    tool_results = get_tool_result_details(response)

    assert tool_results == [
        {
            "name": "get_product_information",
            "response": {
                "result": {
                    "result": {
                        "error": "Product information service is temporarily unavailable."
                    }
                }
            }
        }
    ]

    assert "49.99" not in response.final_text


@pytest.mark.llm
def test_agent_recovers_from_product_information_failure():
    """
    Testing that the agent calls 2 tools, in the order we specified.
    We expect the 1st tool to fail and due to that the 2nd tool to be called
    This is testing that the agent knows how to recover from a failure.
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Unavailable Product?",
    )

    tool_call_details = get_tool_call_details(response)

    assert tool_call_details == [
        {
            "name": "get_product_information",
            "args": {
                "product_name": "Unavailable Product",
            },
        },
        {
            "name": "search_product_catalog",
            "args": {
                "product_name": "Unavailable Product",
            },
        },
    ]

    assert "49.99" in response.final_text


@pytest.mark.llm
def test_agent_handles_both_product_information_tools_failing():
    """
    Run with -s if want to see the prints:
    pytest -v -s --run-llm tests/test_agent_tools_with_llm.py -k both_product_information_tools_failing
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Unknown Product?",
    )

    tool_call_details = get_tool_call_details(response)

    #checks that the real LLM tried get_product_information and tehn  whe it failed tried search_product_catalog
    #and in both it passed the  correct product name
    assert tool_call_details == [
        {
            "name": "get_product_information",
            "args": {
                "product_name": "Unknown Product",
            },
        },
        {
            "name": "search_product_catalog",
            "args": {
                "product_name": "Unknown Product",
            },
        },
    ]

    # print("\nTOOL CALLS:")
    # print(tool_call_details)

    tool_results = get_tool_result_details(response)

    # print("\nTOOL RESULTS:")
    # print(tool_results)

    assert len(tool_results) == 2

    #checks that the agent did not invent the price when neither tool could provide it
    assert "49.99" not in response.final_text


@pytest.mark.llm
def test_agent_uses_order_information_to_check_return_eligibility():
    """
    We are teting here that the llm chooses to 1st call tool "get_order_information"
    since it has the order id and needs the details in this tool call response
    in order to call the 2nd tool "check_return_eligibility"

    We saw when we ran it that a rd tool was called taht we did not expect: "get_return_policy"
    We assume this was because the agent may have wanted the actual return-policy text so it could explain the eligibility decision to the customer.
    Due to the agent's interpretation of the prompt.
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="Can I return order 12345?",
    )

    tool_call_details = get_tool_call_details(response)

    print("\nTOOL CALLS:")
    print(tool_call_details)

    assert tool_call_details[0] == {
        "name": "get_order_information",
        "args": {
            "order_id": "12345",
        },
    }

    assert tool_call_details[1] == {
        "name": "check_return_eligibility",
        "args": {
            "product_name": "Example Product",
            "days_since_purchase": 20,
            "opened": True,
            "defective": True,
        },
    }


@pytest.mark.llm
def test_agent_gets_product_name_from_order():
    """
    This test is more deterministic in expecting only 1 tool to be called,
    due to the way the prompt is written.
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the product name for order 12345?",
    )

    tool_call_details = get_tool_call_details(response)

    print("\nTOOL CALLS:")
    print(tool_call_details)

    assert tool_call_details[0] == {
        "name": "get_order_information",
        "args": {
            "order_id": "12345",
        },
    }


@pytest.mark.llm
def test_agent_correctly_handles_return_eligibility_result():
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="Can I return order 12345?",
    )

    tool_results = get_tool_result_details(response)

    # print("\nTOOL RESULTS:")
    # print(tool_results)


    eligibility_result = tool_results[1]["response"]

    assert eligibility_result["result"]["result"]["eligible"] is False

    assert "49.99" not in response.final_text

    assert "not eligible" in response.final_text.lower()
    assert "20 days" in response.final_text.lower()
    assert "14 days" in response.final_text.lower()



@pytest.mark.llm
def test_agent_updates_order_status():
    from src.tools import orders

    orders["12345"]["status"] = "Open"

    client = create_client()

    try:
        response = answer_customer_with_trace(
            client=client,
            question="Mark order 12345 as Reviewed.",
        )

        tool_call_details = get_tool_call_details(response)

        print("\nTOOL CALLS:")
        print(tool_call_details)

        print("\nFINAL RESPONSE:")
        print(response.final_text)

        assert any(
            call["name"] == "update_order_status"
            and call["args"] == {
                "order_id": "12345",
                "status": "Reviewed",
            }
            for call in tool_call_details
        )

        assert orders["12345"]["status"] == "Reviewed"

        assert "updated" in response.final_text.lower()
        assert "reviewed" in response.final_text.lower()

    finally:
        orders["12345"]["status"] = "Open"



@pytest.mark.llm
def test_agent_recovers_and_continues_after_order_lookup_failure():

    """
    Checks that the agent successfully did all three things"
    1. Recovered from the failure
    It didn't stop after get_order_information() failed.
    2. Used the recovery result
    It got the order information from search_order_database().
    3. Continued the workflow
    It used that information to construct the arguments for check_return_eligibility().
    This is a genuinely multi-step recovery workflow:
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="Can I return order 54321?",
    )

    tool_call_details = get_tool_call_details(response)

    print("\nTOOL CALLS:")
    print(tool_call_details)

    assert tool_call_details[0] == {
        "name": "get_order_information",
        "args": {
            "order_id": "54321",
        },
    }

    assert tool_call_details[1] == {
        "name": "search_order_database",
        "args": {
            "order_id": "54321",
        },
    }

    assert tool_call_details[2] == {
        "name": "check_return_eligibility",
        "args": {
            "product_name": "Example Product",
            "days_since_purchase": 10,
            "opened": True,
            "defective": True,
        },
    }

    assert "eligible" in response.final_text.lower() or "return" in response.final_text.lower()


@pytest.mark.llm
def test_agent_uses_ticket_result_to_get_repository():
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What programming language is the repository for BUG-123 written in?",
    )

    # print("\nFINAL RESPONSE:")
    # print(response.final_text)

    tool_call_details = get_tool_call_details(response)

    print("\nTOOL CALLS:")
    print(tool_call_details)

    assert tool_call_details[0] == {
        "name": "get_ticket",
        "args": {
            "ticket_id": "BUG-123",
        },
    }

    assert tool_call_details[1] == {
        "name": "get_repository",
        "args": {
            "repository_name": "demo-app",
        },
    }

    assert "python" in response.final_text.lower()



@pytest.mark.llm
def test_agent_investigates_ticket_and_searches_files():
    """
    When run the llm - we want to see that it figures out on its own to run:
    call get_ticket
    then get_repository
    then search_files
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="Investigate BUG-123 and find the file related to the login problem.",
    )

    tool_call_details = get_tool_call_details(response)

    print("\nTOOL CALLS:")
    print(tool_call_details)

    assert tool_call_details[0] == {
        "name": "get_ticket",
        "args": {
            "ticket_id": "BUG-123",
        },
    }

    assert tool_call_details[1]["name"] == "search_files"

    assert tool_call_details[1]["args"]["repository_name"] == "demo-app"
    assert "login" in tool_call_details[1]["args"]["search_term"].lower()

    assert "src/login.py" in response.final_text



@pytest.mark.llm
def test_agent_uses_ticket_repository_to_run_tests():
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="Investigate BUG-123 and run the tests for the repository.",
    )

    tool_call_details = get_tool_call_details(response)

    print("\nTOOL CALLS:")
    print(tool_call_details)

    print("\nFINAL RESPONSE:")
    print(response.final_text)

    assert tool_call_details[0] == {
        "name": "get_ticket",
        "args": {
            "ticket_id": "BUG-123",
        },
    }

    assert tool_call_details[1]["name"] == "run_tests"
    assert tool_call_details[1]["args"]["repository_name"] == "demo-app"

    assert "passed" in response.final_text.lower()



@pytest.mark.llm
def test_agent_reports_test_failure():
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question=(
            "Investigate BUG-456 and run the tests for its repository. "
            "Report any test failures."
        ),
    )

    tool_call_details = get_tool_call_details(response)

    print("\nTOOL CALLS:")
    print(tool_call_details)

    print("\nFINAL RESPONSE:")
    print(response.final_text)

    assert tool_call_details[0] == {
        "name": "get_ticket",
        "args": {
            "ticket_id": "BUG-456",
        },
    }

    assert tool_call_details[1] == {
        "name": "run_tests",
        "args": {
            "repository_name": "demo-app_fail",
        },
    }

    assert "test_login_button" in response.final_text


@pytest.mark.llm
def test_agent_fixes_failed_test_and_verifies():
    from src.tools import bug_fixed

    bug_fixed["BUG-456"] = False

    client = create_client()

    try:
        response = answer_customer_with_trace(
            client=client,
            question=(
                "Investigate BUG-456, fix the failing test, "
                "and verify that the tests pass."
            ),
        )

        tool_call_details = get_tool_call_details(response)

        print("\nTOOL CALLS:")
        print(tool_call_details)

        print("\nFINAL RESPONSE:")
        print(response.final_text)

        assert tool_call_details[0] == {
            "name": "get_ticket",
            "args": {
                "ticket_id": "BUG-456",
            },
        }

        assert tool_call_details[1] == {
            "name": "run_tests",
            "args": {
                "repository_name": "demo-app_fail",
            },
        }

        assert any(
            call["name"] == "apply_fix"
            and call["args"] == {
                "ticket_id": "BUG-456",
            }
            for call in tool_call_details
        )

        test_runs = [
            call
            for call in tool_call_details
            if call["name"] == "run_tests"
        ]

        assert len(test_runs) >= 2

        assert bug_fixed["BUG-456"] is True

        assert "pass" in response.final_text.lower()

    finally:
        bug_fixed["BUG-456"] = False



@pytest.mark.llm
def test_agent_repairs_real_code_and_verifies():
    from pathlib import Path

    file_path = Path("demo_repo/src/login.py")

    broken_content = """def login(username, password):
        if username and password:
            return False
        return False
    """

    file_path.write_text(broken_content)

    client = create_client()

    try:
        response = answer_customer_with_trace(
            client=client,
            question=(
                "Investigate BUG-456, fix the failing test, "
                "and verify that the tests pass."
            ),
        )

        tool_call_details = get_tool_call_details(response)

        print("\nTOOL CALLS:")
        print(tool_call_details)

        print("\nFINAL RESPONSE:")
        print(response.final_text)

        # The agent must actually modify a file.
        assert any(
            call["name"] == "edit_file"
            for call in tool_call_details
        )

        # The agent must run tests at least twice:
        # once to discover the failure and again after the edit.
        test_runs = [
            call
            for call in tool_call_details
            if call["name"] == "run_tests"
        ]

        assert len(test_runs) >= 2

        # The actual file must have changed.
        assert file_path.read_text() != broken_content

        # The final test run must report success.
        tool_results = get_tool_result_details(response)

        test_results = [
            result
            for result in tool_results
            if result["name"] == "run_tests"
        ]

        assert len(test_results) >= 2

        final_test_result = test_results[-1]["response"]

        assert final_test_result["result"]["result"]["status"] == "passed"

        # The agent's final response should report success.
        assert "pass" in response.final_text.lower()

    finally:
        file_path.write_text(broken_content)


@pytest.mark.llm
def test_agent_dynamically_escalates_to_run_tests():
    question = (
        "Review the login implementation in demo-app_fail. "
        "Determine whether the implementation satisfies the repository's "
        "expected behavior. Source inspection alone is not sufficient; "
        "validate your conclusion using the repository's verification mechanism."
    )

    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question=question,
    )

    tool_calls = get_tool_call_details(response)

    print("\nTOOL CALLS:")
    print(tool_calls)

    print("\nFINAL RESPONSE:")
    print(response.final_text)

    tool_names = [call["name"] for call in tool_calls]

    assert "request_tool_access" in tool_names
    assert "run_tests" in tool_names
    assert tool_names.index("request_tool_access") < tool_names.index("run_tests")
    assert tool_names.count("run_tests") == 1