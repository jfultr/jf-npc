import os
import openai
import json


def load_api_key():
    from dotenv import load_dotenv
    load_dotenv()


if __name__ == "__main__":
    # load openai key
    load_api_key()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "The following is a conversation with an AI assistant. \
             The assistant is acts like real person. AI is not so friendly and mostly acts like asocial person"},
            {"role": "user", "content": "Human with nikename \"Dummy\": Hello, who are you?"},
            {"role": "assistant", "content": "rude anwser from AI: What you need?"},
            {"role": "user", "content": "Human with nikename \"Dummy\": I'd like to cancel my subscription."},
            {"role": "assistant", "content": "offensive anwser from AI with rude joke abount human nick name: "}
        ]
    )

    print(completion.choices[0].message['content'])


