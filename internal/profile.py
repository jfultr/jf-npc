from typing import Any
from package.database import DatabaseManager


_template = {
    # personal_data
    "клиента_зовут": None,

    # where_to
    "курорт": None,
    "город": None,
    "страна": None,
    "направление": None,
    "тип_туризма": None,

    # when
    "горящий_тур": None,
    "дата_отправления": None,
    "сезон_года": None,
    "дата_возвращения": None,
    "на_сколько_дней": None,

    # count
    "сколько_взрослых_поедут": None,
    "сколько_детей_поедут": None,
    
    # budget
    "бюджет_всей_поездки": None,
    
    # other
    "возраст": None,
    "специальные_пожелания": None,
}


class Profile:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        _client = DatabaseManager().client()
        self.profiles = _client['jfnpc-db']['profiles']

        # get document
        query = {"user_id": user_id}
        projection = {"_id": 0}
        stored_profile = self.profiles.find_one(query, projection)

        # insert new if document doesnt exist
        if stored_profile:
            self._data = stored_profile
        else:
            self._data = _template
            to_db = _template.copy()
            to_db.update({"user_id": user_id})
            self.profiles.insert_one(
                to_db
            )


    def get_properties(self) -> str:
        return ' '.join(self._data.keys())

    def update(self, patch: dict):
        self._data.update(patch)
        filter_query = {"user_id": self.user_id}
        update_query = {"$set": self._data}
        self.profiles.update_one(filter_query, update_query)

    @property
    def data(self):
        return self._data 
