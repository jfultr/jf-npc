from __future__ import annotations
import asyncio
from abc import ABC, abstractmethod
from operator import itemgetter

# langchain powered
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.prompts import SystemMessagePromptTemplate

# langchain rag segment
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.globals import set_verbose
from langchain.globals import set_debug

# cohere powered
import cohere  


set_debug(False)
set_verbose(False)

# utils
from package.common import read_api_key

# design files
from internal.messagelist import MessageList
from internal.profile import Profile
from internal.documentation import QAfile
from internal.question_classification import it_qa_question

from npc.npc import NPC

openai_token = read_api_key("OPENAI_API_KEY")

_greeting_text = """
<данный телеграмм-бот в демо режиме. Могут появляться ошибки>

Привет! Я помогу вам организовать ваше путешествие.
Как мне обращатся к Вам?
""" 


_profiling_template_text = """
Ты туристический кибер-агент, Абеке .
Тебе необходимо узнать у клиента: {propertis}.
Данные, которые уже есть: {data}.
Придерживайся правила описанного ниже.
Привило: {rule}
""" # ...... 
    # + last N messages in chat


_qa_answer_text = """
Сначала используй следующие фрагменты полученного контекста, чтобы ответить на вопрос.
Если не знаешь ответ, просто скажи, что не знаешь. Используй максимум три предложения и будь краткими.

Вопрос: {question}

Контекст: {context}

Ответ:"""


# bind the greeting text
greeting: str = _greeting_text


class CyberQAAssistent:
    def __init__(self) -> None:
        # llm
        self.qa_llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=openai_token
        )

        # template
        self.qa_template =  PromptTemplate.from_template(_qa_answer_text)

        # load context
        doc = QAfile()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
        splits = text_splitter.split_documents(doc)
        vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

        # Retrieve and generate using the relevant snippets of the blog.
        self.retriever = vectorstore.as_retriever()
    
    @staticmethod
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    

    async def answer(self, question: str):
        answer_chain = {
            "context": itemgetter("question") | self.retriever | self.format_docs, 
            "question": itemgetter("question")
        } | self.qa_template | self.qa_llm | StrOutputParser()

        return await answer_chain.ainvoke({"question": question})


class CyberTravelAgent(NPC):
    def __init__(self, messages: MessageList, profile: Profile) -> None:
        # storing data structure implemintation
        self.messages = messages
        self.profile = profile

        # llm to negotiate with client
        self.negotiator = ChatOpenAI(model="gpt-3.5-turbo-0125", api_key=openai_token)

        # llm to classify is there a question in message    
        self.cohere_client = cohere.Client(read_api_key("COHERE_API_KEY"))

        # chain to answer to a qa meassge
        self.qa_assistent = CyberQAAssistent()     
        
        # chat template
        self.chat_context = ChatPromptTemplate.from_messages( 
            [ SystemMessagePromptTemplate.from_template(_profiling_template_text) ] )
    
    def greet(self, _) -> str:
        self.messages.append( AIMessage(content=(_greeting_text)) )
        return greeting
    
    async def a_greet(self, _) -> str:
        raise NotImplemented
    
    def talk(self, _):
        raise NotImplemented

    async def a_talk(self, user_message) -> str:
        # start async data extraction
        asyncio.create_task(self.profile.update(self.messages[-1], user_message))

        # add message to local
        self.messages.append(HumanMessage(content=(user_message)))

        # q&a check
        if it_qa_question(user_message, cohere_client=self.cohere_client):
            print("cyber-travel-agent: q&a branch triggered")
            qa_answer = await self.qa_assistent.answer(user_message)
            answer = await self._chain(qa_answer=qa_answer)
        else:
            # perform a negetiation chain
            answer = await self._chain()

        # store the answer
        self.messages.append(AIMessage(content=answer))
        
        return answer

    async def _chain(self, qa_answer=None):
        # form the context
        #    chat_context ->> system message
        self.chat_context.extend(self.messages[-5:])
        if qa_answer: 
            self.chat_context.append(AIMessage(content=qa_answer))
            self.chat_context.append(HumanMessage(content="ok"))
        self.chat_context.append(AIMessage(content=""))

        # make a chains
        _chain = self.chat_context | self.negotiator | StrOutputParser()    
        
        # wait the answer
        answer = await _chain.ainvoke(
            {
                "propertis": self.profile.get_properties(),
                "data": self.profile.get_state_data(),
                "rule": self.profile.get_rule(),
            }
        )

        if qa_answer: 
            return qa_answer + "\n\n" + answer
        else: 
            return answer
