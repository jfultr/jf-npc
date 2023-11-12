import openai

from internal.contextabc import ThemeContext
from internal.common import read_api_key


name = "Farkhat"
class IntroTheme(ThemeContext):
    def __init__(self, content) -> None:
        self._content = content

    def handle_message(self, message: str) -> str:
        _messages = []
        _messages.append({"role": "user", "content": f"{self._content['userPrefix'].format(name)} {message}"})
        for row in self._content['context']:
            _messages.append(row)
        _messages.append({"role": "assistant", "content": f"{self._content['characterPrefix']}"})
        print(_messages)            
        openai.api_key = read_api_key("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=_messages
        )
        print("\nответ: ", response.choices[0].message['content'], "\n")            
        print(response.usage)



class HrTheme(ThemeContext):
    def __init__(self, content) -> None:
        self._content = content


    def handle_message(self, message: str) -> str:
        _messages = self._content['context']
        _messages.append({"role": "user", "content": f"{self._content['userPrefix']} {message}"})
        _messages.append({"role": "assistant", "content": f"{self._content['characterPrefix']} "})

        print(_messages)            
        openai.api_key = read_api_key("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=_messages
        )

        print(response.choices[0].message['content'])
        print(response.usage)