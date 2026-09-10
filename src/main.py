from src.agent import answer_customer_with_trace
from src.llm_client import create_client


def main():
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Unavailable Product?",
    )

    print(response)


if __name__ == "__main__":
    main()