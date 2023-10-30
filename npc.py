import os
import openai
import json

#internal 
from internal.character import Character
from internal.contextabc import DialogContext

def load_api_key():
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")


if __name__ == "__main__":
    # engineer = Character(
    #     name="syscntr-8",
    #     role="системный инженер",
    #     background=f"Работает в компании TSEN"
    # )

    # engineer_dialog = DialogContext(
    #     readytospeak=f"то в какой компании работает и на какой должности",
    #     confidential=f"о том что в свою крайнюю смену зарегестрировал ошибку на серевере 31",
    #     secret=f"Он уверен, что его скоро уволят. На карйней смене он забыл закрыть порт 5151",
    #     motivation="Скрыть от всех ошибку"
    # )

    
    # exit()
    # load openai key
    openai.api_key = load_api_key()

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


