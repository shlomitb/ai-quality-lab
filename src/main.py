
import os
from google import genai
import json
from dotenv import load_dotenv

from evaluator import evaluate_response


POLICY = """
        Customers may return unopened products within 30 days.

        Opened products may be returned within 14 days
        only if they are defective.

        Digital products cannot be returned.

        Refunds are issued to the original payment method.
        """

def get_prompt(question: str) -> str:
    return f"""
       You are a customer-support assistant.

       Answer the customer's question using ONLY the following
       company return policy.

       Company policy:
       {POLICY}

       Customer question:
       {question}
       
       If the policy does not contain enough information
        to answer the question, do not guess.
       """

ADD_FOR_FUZZY_PROMPT = "If the policy does not explicitly answer the question, make your best guess."

ADD_FOR_CLEAR_PROMPT = """If the policy does not contain enough information
        to answer the question, do not guess.
       """

def ask_llm(client, prompt):
    return client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

def get_data_from_file(file_path: str) -> list[dict] | None:
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        return data

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {file_path}")
        return None


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY was not found in the .env file.")

    client = genai.Client(
        api_key=api_key
    )


    data = get_data_from_file("data/evaluation_cases_small.json")

    if data is None:
        return

    #the 1st 2 we know work. so skip running them for now
    for item in data[:1]:
        question = item["question"]
        evaluation_criteria = item["evaluation_criteria"]

        prompt = f""" You are a customer-support assistant. 
        Answer the customer's question using ONLY the following company return policy. 
        Company policy: 
            {POLICY} 
        Customer question: 
            {question} """

        response = ask_llm(client, prompt)
        ai_response = response.text

        print(f"\nQuestion: {question}")
        print(f"AI: {ai_response}")

        actual_judge_evaluation = evaluate_response(
            client,
            POLICY,
            question,
            ai_response,
            evaluation_criteria
        )

        print(f"Evaluation: {actual_judge_evaluation}")

        assert actual_judge_evaluation == item["expected_judge_evaluation"]

        print("-------------------------------")


    #ask 1 prompt
    #question = "Can I return an unopened product after 20 days?"

    # ai_response = "Yes, you can return an unopened product within 30 days." #PASS
    # ai_response = "No, unopened products cannot be returned." #FAIL
    ai_response = "Yes, you can return an unopened product within 60 days."
    #ai_response = (
    #     "Yes. Since the item has not been opened and it was purchased "
    #     "20 days ago, it is still eligible for return." #PASS
    # )


    # evaluation_criteria = (
    #     "The AI should correctly state that an unopened product "
    #     "can be returned within 30 days." )

    # result = evaluate_response(client, question, ai_response, evaluation_criteria)
    #
    # print("Evaluation:", result)

    # for i in range(4):
    #     result = evaluate_response(
    #         client,
    #         POLICY,
    #         question,
    #         ai_response,
    #         evaluation_criteria
    #     )
    #
    #     print(i + 1, result)

    # prompt = get_prompt(question) + ADD_FOR_CLEAR_PROMPT
    #
    # print(f"prompt: {prompt}")
    # response = ask_llm(client, prompt)
    # print(f"\nQuestion: {question}\n AI: {response.text}")

    # ask multiple prompts
    # print("-------------------------------")
    # for item in data:
    #
    #     question = item["question"]
    #     prompt = get_prompt(question)
    #     response = ask_llm(client, prompt)
    #     print(f"\nQuestion: {question}\n AI: {response.text}")
    #
    #     print("-------------------------------")





if __name__ == "__main__":
    main()