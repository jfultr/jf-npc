from datetime import datetime
from package.database import DatabaseManager
from langchain_core.messages import BaseMessage, messages_from_dict
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


def adaptor_mongo_to_lc(document: dict) -> BaseMessage:
    if document["type"] == "system":
        return SystemMessage(content=(document["content"]))
    if document["type"] == "ai":
        return AIMessage(content=(document["content"]))
    if document["type"] == "human":
        return HumanMessage(content=(document["content"]))


class MessageList(list):
    def __init__(self, _id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._id = _id
        _client = DatabaseManager().client()
        self._messages = _client['jfnpc-db']['messages']
        stored_messages = self._messages.find({"chat_id": self._id})
        
        for message in stored_messages:
            self._adapted_append(adaptor_mongo_to_lc(message))

    def _adapted_append(self, message):
        super().append(message)
     
    # override
    def append(self, item: BaseMessage):
        self._adapted_append(item)
        document = {
            "chat_id": self._id,
            "timestamp": datetime.now(),
            "type": item.type,
            "content": item.content
        }

        self._messages.insert_one(document)

    # override
    def extend(self, items):
        for item in items:
            self.append(item)
