from __future__ import annotations
import asyncio

# gpt powered
from openai import AsyncOpenAI

# utils
from package.common import read_api_key

# design files
from internal.messagelist import MessageList


openai_token = read_api_key("OPENAI_API_KEY")

_starting_context = "Ты онлайн турестический агент.\n" \
                    "Тебе необходимо узнать у клиента: возраст, пункт отправления, пункт прибытия, количество людей.\n" \
                    "Задавай вопросы пока не узнаешь ответы на все вопросы. По мере заполняй профайл клиента\n"

_greeting_text = "Привет! Я помогу вам организовать ваше путешествие.\n" \
                 "Давайте начнем с вашего возраста. Сколько вам лет?"

# bind the greeting text
greeting: str = _greeting_text

# agents cache
agents = {}


def get_travel_agent(_id: int) -> TravelAgent:
    if _id in agents:
        return agents[_id]
    else:
        agent = TravelAgent(MessageList(str(_id)))
        agents.update({_id: agent})
        return agent


class TravelAgent:    
    def __init__(self, messages: MessageList) -> None:
        # openai client
        self.client = AsyncOpenAI(
            # This is the default and can be omitted
            api_key=openai_token
        )

        # storing data structure implemintation
        self.messages = messages
    
    def handle_user_greeting(self) -> str:
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
        return greeting

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
        self.messages.append(
            {
                "role": "assistant",
                "content": gpt_response
            }
        )
        
        # start async data extraction
        asyncio.create_task(self._data_extraction(message))
        return gpt_response

    async def _data_extraction(self, message):
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
        print(comp.choices[0].message.content)



