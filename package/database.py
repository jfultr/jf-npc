import pymongo
import bson

"""
"messages": 
{
    "chat_id": int
    "role": {}
    "content": []
},
...
    
"""

class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = pymongo.MongoClient("mongodb://localhost:27017/")
        return cls._instance

    def client(self):
        return self._client
    
    
def is_chat_stored(_id: str):
    _client = DatabaseManager().client()
    messages = _client['jfnpc-db']['messages']
    stored_messages = messages.find_one({"chat_id": _id})
    if stored_messages is None:
        return False
    else:
        return True