from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

load_dotenv()

client = InferenceClient(
    token=os.getenv("HUGGINGFACE_TOKEN")
)

response = client.chat_completion(
    model="Qwen/Qwen3-8B",
    messages=[
        {
            "role": "user",
            "content": "Hello"
        }
    ],
    max_tokens=20
)

print(response)