from __future__ import annotations
import asyncio
import json

# langchain powered
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate

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

_json_template = { "Возраст": None, "Пункт отправления": None, "Пункт прибытия": None, "Количество людей" : None }

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
        # storing data structure implemintation
        self.messages = messages

        # openai client
        self.model = ChatOpenAI(
            model="gpt-4",
            api_key=openai_token
        )
        
        # chat tamplate
        self.system_context = SystemMessagePromptTemplate.from_template("{system_context}")

        # extraction tamplate
        self.extraction_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=("Ты анализатор текста. Ты аналезируешь диалог AI и пользователя. "
                                       "Тебе нужно заполнить json соответсвующей информацией из вопроса и ответа")),
                HumanMessagePromptTemplate.from_template("AI задал вопрос: {question}"),
                HumanMessagePromptTemplate.from_template("Клиент дал ответ: {answer}"),
                HumanMessagePromptTemplate.from_template("Заполни данный json: {json_tamplate}"),
            ]
        )
        # answer parser
        self.parser = StrOutputParser()
    
    def handle_user_greeting(self) -> str:
        self.messages.append( AIMessage(content=(_greeting_text)) )
        return greeting

    async def handle_user_message(self, user_message) -> str:
        # remember prev ai message
        prev_ai_message = self.messages[-1]

        # add message to local
        self.messages.append(HumanMessage(content=(user_message)))

        # form the context
        chat_context = ChatPromptTemplate.from_messages( [ self.system_context ] )
        chat_context.extend(self.messages[-10:])

        # make a chain
        answer_chain = chat_context | self.model | self.parser

        # wait the answer
        answer = await answer_chain.ainvoke({"system_context": _starting_context})

        # store the answer
        self.messages.append(AIMessage(content=answer))
        
        # start async data extraction
        asyncio.create_task(self._data_extraction(prev_ai_message, user_message))
        return answer

    async def _data_extraction(self, question, answer):
        extrraction_chain = self.extraction_template | self.model | self.parser

        extracted = await extrraction_chain.ainvoke(
            {
                "question": question,
                "answer": answer,
                "json_tamplate": json.dumps(_json_template)
            }
        )
        print(extracted)



