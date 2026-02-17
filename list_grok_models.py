import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        print("ERROR: GROK_API_KEY not found in .env")
        return

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
    )

    try:
        models = client.models.list()
        print("\n--- Available Models ---")
        for model in models:
            print(f"- {model.id}")
    except Exception as e:
        print(f"ERROR: Failed to list models: {e}")

if __name__ == "__main__":
    list_models()
