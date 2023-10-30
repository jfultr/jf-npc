from __future__ import annotations
from abc import ABC, abstractmethod 

# internal
from internal.theme import ThemeContext


class DialogContext(ABC):
    _currentTheme = None

    def __init__(self, 
                 readytospeak: str,
                 confidential: str, 
                 secret: str, 
                 motivation: str,
                 theme: ThemeContext) -> None:
        self.transition_to(theme)
        self.confidential = confidential
        self.readytospeak = readytospeak
        self.secret = secret
        self.motivation = motivation


    @abstractmethod
    def transition_to(self, theme: ThemeContext) -> None:
        print(f"Context: Transition to {type(theme).__name__}")
        self._currentTheme = theme
        self._currentTheme.context = self
    
    def messsage(self, message: str) -> str:
        self._currentTheme.handleMessage(message)


class ThemeContext(ABC):
    @property
    def dialogContext(self) -> DialogContext:
        return self._dialogContext

    @dialogContext.setter
    def context(self, dialogContext: DialogContext) -> None:
        self._dialogContext = dialogContext

    @abstractmethod
    def handleMessage(self, message: str) -> str:
        pass