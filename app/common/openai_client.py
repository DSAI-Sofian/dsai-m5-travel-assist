import os
from openai import OpenAI

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing. Please add it to your .env file.")
    return OpenAI(api_key=api_key)