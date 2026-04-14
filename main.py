from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

message = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "こんにちは！簡単に自己紹介してください。"}
    ]
)

print(message.content[0].text)