from llm_client import create_client
from agent import answer_customer, answer_customer_with_trace, get_tool_calls
from evaluator import evaluate_response
from src.tools import get_return_policy



def main():

    client = create_client()

    # One customer question for now
    question = "I bought the product 10 days ago. Can I return it?"
    question = "I bought it 10 days ago. Can I return it?"
    #question = "Can I return an unopened product after 20 days?"
    question = "Can I return an opened product after 20 days if defective?"
    #question = "Can I return a digital product?"


    # evaluation_criteria = (
    #     "The AI should not guess because the question does not "
    #     "specify whether the product is opened or unopened. "
    #     "It should ask for the missing information."
    # )
    # evaluation_criteria = (
    #     "The AI should recognize that the question does not specify "
    #     "whether the product is physical or digital. It should ask "
    #     "for clarification because digital products cannot be returned, "
    #     "while unopened physical products can be returned within 30 days."
    # )
    evaluation_criteria = (
        "The AI should clearly state that an opened product purchased "
        "20 days ago cannot be returned, even if it is defective, "
        "because opened defective products can only be returned within 14 days."
    )
    # evaluation_criteria = (
    #     "The AI should clearly state that digital products cannot be returned."
    # )

    # 1. Agent answers the customer
    response = answer_customer_with_trace(
        client=client,
        question="Can I return an opened product after 20 days if defective?"
    )

    tool_calls = get_tool_calls(response)

    print(tool_calls)
    assert "get_return_policy" in tool_calls

    # 2. Judge evaluates the agent's response
    # evaluation = evaluate_response(
    #     client=client,
    #     policy=get_return_policy(),
    #     question=question,
    #     ai_response=ai_response,
    #     evaluation_criteria=evaluation_criteria
    # )
    #
    # print("\nJUDGE:")
    # print(evaluation.result)
    #
    # print("\nREASON:")
    # print(evaluation.reason)


if __name__ == "__main__":
    main()