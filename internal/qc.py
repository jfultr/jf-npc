from __future__ import annotations
from abc import ABC, abstractmethod

_current_implementation = "Cohere"

if _current_implementation == "Cohere":
    import cohere  
    from cohere.responses.classify import Example
    from langchain_core.runnables import chain

if _current_implementation == "OpenAi":
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser

from package.common import read_api_key


def get_question_classificator() -> QC:
    if _current_implementation == "Cohere":
        return QCCohere(read_api_key("COHERE_API_KEY"))
    if _current_implementation == "OpenAi":
        return QCOpenAi(read_api_key("OPENAI_API_KEY"))
    else:
        raise "qc implemantation not find"
    

# question classification base class
class QC(ABC):
    def __init__(self, api_key) -> None:
        super().__init__()
        self.api_key = api_key

    @abstractmethod
    def get_chain(self):
        pass


_question_classifictor_text = """
Учитывая сообщение пользователя ниже, классифицируй иметься ли в сообщении вопрос.
Не отвечайте более чем одним словом.
Отвечай только `yes`, `no`

<message>
{message}
</message>

Classification:"""


class QCOpenAi(QC):
    def __init__(self, api_key) -> None:
        super().__init__(api_key)
        self._client = ChatOpenAI(model="gpt-3.5-turbo", api_key=self.api_key, temperature=0)
        self.qc_template = PromptTemplate.from_template(_question_classifictor_text)

    def get_chain(self):
        qc_chain = self.qc_template | self._client | StrOutputParser()  
        return qc_chain


qc_examples=[
    Example("Что такое чартер?", "q&a reqest"),
    Example("Горящий тур?", "q&a reqest"),
    Example("Что такое Горящий тур?", "q&a reqest"),
    Example("Какие документы нужны", "q&a reqest"),
    Example("Как я могу оплатить", "q&a reqest"),
    Example("Что входит в стоймость пакета?", "q&a reqest"),
    Example("Туркод", "q&a reqest"),
    Example("Цена поменялась", "q&a reqest"),

    Example("Да, я хочу", "common"),
    Example("Япония", "common"),
    Example("думаю, полечу в Канаду", "common"),
    Example("23", "common"),
    Example("Фархат", "common"),
    Example("Дубай. Через неделю", "common"),
    Example("Хочу ограничется бюджетом в 1000$", "common"),
    Example("Как тебя зовут?", "common"),
    Example("Как дела?", "common")

]


class QCCohere(QC):
    def __init__(self, api_key) -> None:
        super().__init__(api_key)
        self._client = cohere.Client(self.api_key)     
 
    def get_chain(self):
        # return a anonimus func
        @chain
        def _qc_chain(text):
            response = self._client.classify(  
                model='embed-multilingual-v2.0',  
                inputs=[text["message"]],  
                examples=qc_examples)

            if  response.classifications[0].predictions[0] == "q&a reqest":
                return "yes"
            else:
                return "no"
            
        return _qc_chain

