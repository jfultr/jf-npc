import asyncio

# gpt powered
from openai import AsyncOpenAI

# utils
from package.common import read_api_key
from package.messagelist import MessageList

openai_token = read_api_key("OPENAI_API_KEY")

_starting_context = "Ты онлайн турестический агент.\n" \
                    "Тебе необходимо узнать у клиента: возраст, пункт отправления, пункт прибытия, количество людей.\n" \
                    "Задавай вопросы пока не узнаешь ответы на все вопросы. По мере заполняй профайл клиента\n"

_greeting_text = "Привет! Я помогу вам организовать ваше путешествие.\n" \
        "Давайте начнем с вашего возраста. Сколько вам лет?"


class TravelAgent:
    def __init__(self, id) -> None:
        self._id = id

        # openai client
        self.client = AsyncOpenAI(
            # This is the default and can be omitted
            api_key=openai_token
        )

        # bind the greeting text
        self.greeting = _greeting_text

        # storing data structure implemintation
        self.messages = MessageList(id)

        if(len(self.messages) == 0):
            self.messages.extend(
                [
                    {
                        "role": "system",
                        "content": _starting_context
                    }, 
                    {
                        "role": "assistant",
                        "content": _greeting_text
                    }
                ]
            )


    @property
    def id(self):
        return self._id
    
    async def handle_user_message(self, message) -> str:
        # add message to chat context
        self.messages.append(
            {
                "role": "user",
                "content": message
            }
        )

        # wait the answer
        comp = await self.client.chat.completions.create(
            messages=self.messages,
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
                            f"вопрос: {self.messages[-2]['content']}"
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

            self.messages.append(
                {
                    "role": "assistant",
                    "content": gpt_response
                }
            )
            print(comp.choices[0].message.content)

        asyncio.create_task(data_extraction())
        print(self.messages)
        return gpt_response

