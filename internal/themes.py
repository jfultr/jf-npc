import openai

from internal.contextabc import ThemeContext
from internal.common import read_api_key


class IntroTheme(ThemeContext):
    def __init__(self, content) -> None:
        self._content = content


    def handle_message(self, message: str) -> str:
        _messages = [
            {"role": "system", "content": f"В чате учавсвует {self._dialogContext.character.name}. {self._dialogContext.character.background}."},
            {"role": "system", "content": f"{self._content['introContext']}\n"},
            {"role": "user", "content": f"незнакомец: {message}"},
            {"role": "assistant", "content": f"{self._dialogContext.character.name}: "}
        ]

        print(_messages)            
        openai.api_key = read_api_key("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=_messages
        )

        print(response.choices[0].message['content'])
        print(response.usage)