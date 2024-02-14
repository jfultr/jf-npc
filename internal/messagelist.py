import pymongo
import bson

from package.database import DatabaseManager


class MessageList(list):
    def __init__(self, _id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._id = _id
        _client = DatabaseManager().client()
        self._messages = _client['jfnpc-db']['messages']
        stored_messages = self._messages.find({"chat_id": self._id})
        for message in stored_messages:
            self._adapted_append(message)

    def _adapted_append(self, message):
        super().append(
            {
                "role": message["role"],
                "content": message["content"]
            }
        )
     
    # override
    def append(self, item: dict):
        self._adapted_append(item)
        item.update({"chat_id": self._id})
        self._messages.insert_one(item)

    # override
    def extend(self, items):
        for item in items:
            self.append(item)
