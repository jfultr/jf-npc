import pymongo
import bson

class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = pymongo.MongoClient("mongodb://localhost:27017/")
        return cls._instance

    def client(self):
        return self._client


class MessageList(list):
    def __init__(self, _id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._id = _id
        _client = DatabaseManager().client()
        self._messages = _client['jfnpc-db']['messages']
        stored_messages = self._messages.find({"chat_id": self._id})
        for message in stored_messages:
            print(message)
            super().append(message)

    # override
    def append(self, item: dict):
        super().append(item)
        item.update({"chat_id": self._id})
        self._messages.insert_one(item)

    # override
    def extend(self, items):
        super().extend(items)

        for item in items:
            self.append(item)
