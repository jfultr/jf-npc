from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional
from package.database import DatabaseManager
from yaml import safe_load
import json

# utils
from package.common import read_api_key

# langchain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser

openai_token = read_api_key("OPENAI_API_KEY")


class Profile:
    _state: State = None

    def __init__(self, user_id:str) -> None:
        self.user_id = user_id
        _client = DatabaseManager().client()
        self.profiles = _client['jfnpc-db']['profiles']

        # get document
        query = {"user_id": user_id}
        projection = {"_id": 0}
        stored_profile = self.profiles.find_one(query, projection)
        
        # load rules document
        with open("content/rules-stage.yaml", 'r') as file:
            # Load YAML data from the file
            self._rules = safe_load(file)

        # insert new if document doesnt exist
        if stored_profile:
            self._data = stored_profile
        else:
            self._data = self._load_keys(self._rules)
            to_db = self._data.copy()
            to_db.update({"user_id": user_id})
            self.profiles.insert_one(
                to_db
            )

        # llm to extract usefull information for profile 
        self.extractor = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=openai_token,
            temperature=0.1
        )

        # start profiling from this state
        self.transition_to(WhereToProfiling())

    def _load_keys(self, document: dict) -> dict:
        result = {}
        for stage_key in document:
            result.update(document[stage_key]["properties"])
        return result

    def transition_to(self, state: State):
        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self

    def get_properties(self):
        return ' '.join("\""+ key + "\"" for key in self._rules[self._state.get_key()]["properties"].keys())

    def get_state_data(self):
        return str(self._data)
    
    def get_rule(self):
        return ' '.join(self._rules[self._state.get_key()]["rule"])
    
    async def update(self, question, answer):
        _extraction_template_chat = [
            SystemMessage(content=(
                "Ты анализатор текста. Ты аналезируешь диалог AI и Клиента. "
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

        self.extraction_template = ChatPromptTemplate.from_messages(_extraction_template_chat)
        extrraction_chain = self.extraction_template | self.extractor | StrOutputParser()
        patch = await extrraction_chain.ainvoke(
            {
                "question": question,
                "answer": answer,
                "json_template": json.dumps(self.data)
            }
        )
    
        state_or_none = self._state.transition_request()
        if state_or_none is not None:
            self.transition_to(state_or_none)

        self._update(json.loads(patch))
        print(patch)

    def _update(self, patch: dict):
        self._data.update(patch)
        filter_query = {"user_id": self.user_id}
        update_query = {"$set": self._data}
        self.profiles.update_one(filter_query, update_query)

    @property
    def data(self):
        return self._data 


class State(ABC):
    @property
    def context(self) -> Profile:
        return self._context

    @context.setter
    def context(self, context: Profile) -> None:
        self._context = context

    @abstractmethod
    def get_key(self):
        pass

    @abstractmethod
    def transition_request(self) -> None:
        pass


class PersonalDataProfiling(State):
    _key: str = "personal_data"
    
    def get_key(self):
        return self._key
    
    def transition_request(self, question, answer) -> dict:
        return WhereToProfiling()


class WhereToProfiling(State):
    _key: str = "where_to"
    
    def get_key(self):
        return self._key
    
    def transition_request(self):
        properties = self._context._data
        if ((properties["курорт"]) \
            or (properties["город"]) \
            or (properties["страна"] and properties["тип_туризма"]) \
            or (properties["направление"] and properties["тип_туризма"])
        ):
            return WhenProfiling()
        else:
            return None


class WhenProfiling(State):
    _key: str = "when"

    def get_key(self):
        return self._key
    
    def transition_request(self):
        properties = self._context._data
        if ((properties["это_будет_горящий_тур"] is True and properties["дата_отправления"] and properties["на_сколько_дней"]) \
            or (properties["это_будет_горящий_тур"] is False and (properties["дата_отправления"] or properties["сезон_года"]) and properties["на_сколько_дней"]) \
        ):
            return CountProfiling()
        else:
            return None


class CountProfiling(State):
    _key: str = "count"

    def get_key(self):
        return self._key
    
    def transition_request(self):
        properties = self._context._data
        if (properties["сколько_взрослых_поедут"] and properties["сколько_детей_поедут"]):
            return BudgetProfiling()
        else:
            return None


class BudgetProfiling(State):
    _key: str = "budget"

    def get_key(self):
        return self._key

    def transition_request(self):
        properties = self._context._data
        if (properties["бюджет_поездки"]):
            return BudgetProfiling()
        else:
            return None
        

class OtherProfiling(State):
    _key: str = "other"

    def get_key(self):
        return self._key
    
    def transition_request(self):
        return None
