import os
import asyncio

# gpt powered
from openai import AsyncOpenAI


def load_api_key(name):
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv(name)


openai_token = load_api_key("OPENAI_API_KEY")
_messages = []


# get_age
# get_city_from
# get_city_to
# get_people_count
# cancel
# error

_starting_context = "Ты онлайн турестический агент.\n" \
                    "Тебе необходимо узнать у клиента: возраст, пункт отправления, пункт прибытия, количество людей.\n" \
                    "Задавай вопросы пока не узнаешь ответы на все вопросы. По мере заполняй профайл клиента\n"

_greeting_text = "Привет! Я помогу вам организовать ваше путешествие.\n" \
        "Давайте начнем с вашего возраста. Сколько вам лет?"

_messages = [
    {
        "role": "system",
        "content": _starting_context
    },
    {
        "role": "assistant",
        "content": _greeting_text
    }
]


class TravelAgent:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            # This is the default and can be omitted
            api_key=openai_token
        )
        self.greeting = _greeting_text

    async def handle_user_message(self, message) -> str:
        # add message to chat context
        _messages.append(
            {
                "role": "user",
                "content": message
            }
        )

        # wait the answer
        comp = await self.client.chat.completions.create(
            messages=_messages,
            model="gpt-3.5-turbo",
        )

        # store the answer
        gpt_response = comp.choices[0].message.content

        # start async data extraction
        async def data_extraction():
            comp = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": \
                            f"вопрос: {_messages[-2]['content']}"
                            f"ответ: {message}\n" \
                            "Прочитай эти сообщения и заполни эти поля. Оставляй поля пустыми, если данные не указаны\n" \
                            "Возраст: <int>\n" \
                            "Пункт отправления: <string>\n" \
                            "Пункт прибытия: <string>\n" \
                            "Количество людей: <int>\n" \
                    }
                ],
                model="gpt-3.5-turbo",
            )

            _messages.append(
                {
                    "role": "assistant",
                    "content": gpt_response
                }
            )
            print(comp.choices[0].message.content)

        asyncio.create_task(data_extraction())
        print(_messages)
        return gpt_response

