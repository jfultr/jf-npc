from __future__ import annotations
from abc import ABC, abstractmethod 

from internal.character import Character


class DialogContext():
    _currentTheme = None

    def __init__(self, 
                 theme: ThemeContext,
                 character: Character,
                 content: dir,
                 readytospeak: str,
                 confidential: str, 
                 secret: str, 
                 motivation: str) -> None:
        self.transition_to(theme)
        self.content = content
        self.character = character
        self.confidential = confidential
        self.readytospeak = readytospeak
        self.secret = secret
        self.motivation = motivation

    def transition_to(self, theme: ThemeContext) -> None:
        print(f"Context: Transition to {type(theme).__name__}")
        self._currentTheme = theme
        self._currentTheme.context = self
    
    def handle_message(self, message: str) -> str:
        self._currentTheme.handle_message(message)


def createDialogJson(theme: ThemeContext, character: Character, content: dir) -> DialogContext:
    return DialogContext(
        theme=theme,
        character = character,
        content=content,
        readytospeak=content['readytospeak'],
        confidential=content['confidential'], 
        secret=content['secret'], 
        motivation=content['motivation'],
    )


# theme interface
class ThemeContext(ABC):
    @property
    def dialogContext(self) -> DialogContext:
        return self._dialogContext

    @dialogContext.setter
    def context(self, dialogContext: DialogContext) -> None:
        self._dialogContext = dialogContext

    @abstractmethod
    def handle_message(self, message: str) -> str:
        pass