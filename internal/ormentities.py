from typing import List
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


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
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    age: Mapped[int] = mapped_column(Integer)

    chat: Mapped["Chat"] = relationship(back_populates='user')

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id!r})"