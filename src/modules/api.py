from openai import OpenAI
import os

def create_client(timeout=60, max_retries=0):

    print(
        "Created client:\n"
        f" - Timeout: {timeout}\n"
        f" - Max retries: {max_retries}\n"
    )

    return OpenAI(
        api_key=os.getenv("OPEN_AI_TEST_KEY"),
        timeout=timeout,
        max_retries=max_retries
    )