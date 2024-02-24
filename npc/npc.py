from abc import ABC, abstractmethod

class NPC(ABC):
    @abstractmethod
    def greet(input: str) -> str:
        pass

    @abstractmethod
    def talk(input: str) -> str:
        pass

    @abstractmethod
    async def a_greet(input: str) -> str:
        pass

    @abstractmethod
    async def a_talk(input: str) -> str:
        pass