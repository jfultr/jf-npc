from __future__ import annotations
import asyncio
import json
from operator import itemgetter

# langchain powered
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate

# langchain rag segment
from langchain_core.runnables import RunnableBranch
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.globals import set_verbose
from langchain.globals import set_debug

set_debug(True)
set_verbose(True)

# utils
from package.common import read_api_key

# design files
from internal.messagelist import MessageList
from internal.profile import Profile
from internal.documentation import QAfile

openai_token = read_api_key("OPENAI_API_KEY")

_greeting_text = """
<данный телеграмм-бот в демо режиме. Могут появляться ошибки>

Привет! Я помогу вам организовать ваше путешествие.
Как мне обращатся к Вам?
""" 


_profiling_template_text = """
Ты онлайн туристический агент.
Тебе необходимо узнать у клиента: {propertis}.
Задавай вопросы пока не узнаешь ответы на все вопросы.
Не пытайся отвечать на вопросы
""" # ...... 
    # + last N messages in chat


_question_classifictor_text = """
Учитывая сообщение пользователя ниже, классифицируй иметься ли в сообщении вопрос.
Не отвечайте более чем одним словом.
Отвечай только `yes`, `no`

<message>
{message}
</message>

Classification:"""


_qa_answer_text = """
Сначала используй следующие фрагменты полученного контекста, чтобы ответить на вопрос.
Если не знаешь ответ, просто скажи, что не знаешь. Используй максимум три предложения и будь краткими.

Вопрос: {question}

Контекст: {context}

Ответ:"""


_qa_extension_text = """
Тебе необходимо совместить Q&A ответ и сообщение от ИИ бота, таким образом чтобы это выглядило локонично

Q&A ответ: {qa_answer}
сообщение от ИИ бота: {negotiator_answer}
локоничный ответ:"""


_extraction_template_chat = [
    SystemMessage(content=(
        "Ты анализатор текста. Ты аналезируешь диалог AI и пользователя. "
        "Тебе нужно заполнить json соответсвующей информацией ответа Клиента")
    ),
    AIMessagePromptTemplate.from_template(
        "AI задал вопрос: {question}"
    ),
    HumanMessagePromptTemplate.from_template(
        "Клиент дал ответ: {answer}"
    ),
    HumanMessagePromptTemplate.from_template(
        "Заполни данный json в формате utf-8: {json_template}"
    ),
]


# bind the greeting text
greeting: str = _greeting_text

# agents cache
agents = {}


def get_travel_agent(chat_id: int, user_id: int) -> TravelAgent:
    if chat_id in agents:
        return agents[chat_id]
    else:
        agent = TravelAgent(
            MessageList(str(chat_id)),
            Profile(str(user_id))
        )
        agents.update({chat_id: agent})
        return agent


class TravelAgent:    
    def __init__(self, messages: MessageList, profile: Profile) -> None:
        # storing data structure implemintation
        self.messages = messages
        self.profile = profile

        # llm to negotiate with client
        self.negotiator = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=openai_token
        )

        # llm to classify is there a question in message
        self.qc_llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=openai_token,
            temperature=0
        )

        # llm to classify is there a question in message
        self.qa_llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=openai_token
        )

        self.qa_ext_llm = ChatOpenAI(
            model="gpt-4-0125-preview",
            api_key=openai_token,
            temperature=0.5
        )

        # llm to extract usefull information for profile 
        self.extractor = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=openai_token,
            temperature=0.1
        )
        
        # chat template
        self.chat_context = ChatPromptTemplate.from_messages( 
            [ SystemMessagePromptTemplate.from_template(_profiling_template_text) ] )
        
        # question classificator template
        self.qc_template = PromptTemplate.from_template(_question_classifictor_text)

        # qa template
        self.qa_template =  PromptTemplate.from_template(_qa_answer_text)
        self.qa_ext_template = PromptTemplate.from_template(_qa_extension_text)

        # extraction template
        self.extraction_template = ChatPromptTemplate.from_messages(_extraction_template_chat)
    
    def handle_user_greeting(self) -> str:
        self.messages.append( AIMessage(content=(_greeting_text)) )
        return greeting

    async def handle_user_message(self, user_message) -> str:
        # remember prev ai message
        prev_ai_message = self.messages[-1]

        # add message to local
        self.messages.append(HumanMessage(content=(user_message)))

        # form the context
        self.chat_context.extend(self.messages[-10:])

        # load context
        doc = QAfile()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
        splits = text_splitter.split_documents(doc)
        vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

        # Retrieve and generate using the relevant snippets of the blog.
        retriever = vectorstore.as_retriever()

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # message --> neg_chain __
        #                         \
        #                           > --> if(qc_chain==yes) --> qa_chain --> qa_ext_chain --> out
        #                          /      if(qc_chain==no)  --> out 
        # message --> qc_chain  __/
        
        
        # make a chains
        neg_chain = self.chat_context | self.negotiator | StrOutputParser()                                                          
        qc_chain = self.qc_template | self.qc_llm | StrOutputParser()       
        qa_answer_chain = self.qa_template | self.qa_llm | StrOutputParser()
        qa_ext_chain = self.qa_ext_template | self.qa_ext_llm | StrOutputParser()
        
        # 1. run parallel negotiator and question classification
        first_parallel_chain = {
            "negotiator_answer": neg_chain, 
            "is_there_question": qc_chain, 
            "message": itemgetter("message")   
        }
        
        # 2. if qc: "yes" -> read context 
        qa_passthrough_chain = {
            "context": itemgetter("message") | retriever | format_docs, 
            "question": itemgetter("message"),
            "negotiator_answer": itemgetter("negotiator_answer")
        } 
        
        # 3. if qc: "yes" -> read context -> add q&a answer to negotiator answer -> full answer
        qa_ext_passthrough_chain = {
            "qa_answer": qa_answer_chain, 
            "negotiator_answer": itemgetter("negotiator_answer")
        } 
        
        full_chain = first_parallel_chain | RunnableBranch (
            # if message have a qestion
            (lambda x: "yes" in x["is_there_question"].lower(), 
                qa_passthrough_chain | (qa_ext_passthrough_chain | qa_ext_chain) ),
            
            # if message not have a qestion
            (lambda x: "no" in x["is_there_question"].lower(), 
                lambda x: x["negotiator_answer"]),

            # default
            lambda x: x["negotiator_answer"]
        )
        
        # wait the answer
        answer = await full_chain.ainvoke(
            {
                "propertis": self.profile.get_properties(),
                "message": user_message
            }
        )

        # store the answer
        self.messages.append(AIMessage(content=answer))
        
        # start async data extraction
        asyncio.create_task(self._data_extraction(prev_ai_message, user_message))
        return answer

    async def _data_extraction(self, question, answer):
        extrraction_chain = self.extraction_template | self.extractor | StrOutputParser()

        extracted = await extrraction_chain.ainvoke(
            {
                "question": question,
                "answer": answer,
                "json_template": json.dumps(self.profile.data)
            }
        )
        self.profile.update(json.loads(extracted))
        print(extracted)
