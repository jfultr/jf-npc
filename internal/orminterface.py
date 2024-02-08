from typing import List
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy import String, Integer, ARRAY
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

# from sqlalchemy import Column, Integer, ARRAY, String
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

# class Chat(Base):
#     __tablename__ = 'chats'

#     id = Column(Integer, primary_key=True)
#     chat_id = Column(Integer)
#     chat = Column(ARRAY(String))

class Base(DeclarativeBase):
    pass


class Chat(Base):
    __tablename__ = "chat"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer)

    # chat has many messages
    chat_history: Mapped[List[str]] = relationship(back_populates='chat')
    
    # relationship one chat one user
    user: Mapped["User"] = relationship(back_populates='chat')

    def __repr__(self) -> str:
        return f"Chat(chat_id={self.chat_id!r})"


class Message(Base):
    __tablename__ = "message"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat: Mapped["Chat"] = relationship(back_populates='message')
    # timestamp: 



class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    age: Mapped[int] = mapped_column(Integer)

    chat: Mapped["Chat"] = relationship(back_populates='user')

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id!r})"