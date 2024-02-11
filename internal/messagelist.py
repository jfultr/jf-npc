# orm
from sqlalchemy import create_engine
from internal.ormentities import Base
from internal.ormentities import Chat, Message, User
from sqlalchemy.orm import Session


class SingletonMeta(type):
    """
    В Python класс Одиночка можно реализовать по-разному. Возможные способы
    включают себя базовый класс, декоратор, метакласс. Мы воспользуемся
    метаклассом, поскольку он лучше всего подходит для этой цели.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Данная реализация не учитывает возможное изменение передаваемых
        аргументов в `__init__`.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Orm(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._engine = create_engine("sqlite://", echo=True)
        Base.metadata.create_all(self._engine)

    @property
    def engine(self):
        return self._engine
    

class MessageList(list):
    def __init__(self, id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ormengine = Orm().engine
        from sqlalchemy import select

        session = Session(self.ormengine)
        stmt = select(Chat)

        for user in session.scalars(stmt):
            print(user)

    # override
    def append(self, item):
        super().append(item)
    
    # override
    def extend(self, item):
        super().extend(item)