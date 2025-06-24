import os
import random

try:
    import openai
except ImportError:  # pragma: no cover - openai might not be installed
    openai = None

API_KEY = os.getenv("OPENAI_API_KEY")
USE_MOCK = not API_KEY or API_KEY.startswith("sk-demo")

if not USE_MOCK and openai:
    openai.api_key = API_KEY


def get_completion(messages):
    """Return a chat completion message object."""
    if USE_MOCK or not openai:
        return {"content": "This is a mock response."}

    resp = openai.ChatCompletion.create(model="gpt-4o", messages=messages)
    return resp["choices"][0]["message"]
