
import os
from google import genai
import json
from dotenv import load_dotenv


POLICY = """
        Customers may return unopened products within 30 days.

        Opened products may be returned within 14 days
        only if they are defective.

        Digital products cannot be returned.

        Refunds are issued to the original payment method.
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


    data = get_data_from_file("evaluation_cases.json")

    if data is None:
        return

    for item in data:

        question = item["question"]

        prompt = f"""
            You are a customer-support assistant.
    
            Answer the customer's question using ONLY the following
            company return policy.
    
            Company policy:
            {POLICY}
    
            Customer question:
            {question}
            """
        response = ask_llm(client, prompt)
        print(f"\nQuestion: {question}\n AI: {response.text}")

        print("-------------------------------")





if __name__ == "__main__":
    main()