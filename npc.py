import json

#internal 
from internal.character import craeteCharacterJson
from internal.contextabc import createDialogJson
from internal.themes import IntroTheme


if __name__ == "__main__":
    content = json.load(open('content/demo.json'), )

    engineer_dialog = createDialogJson(
        theme=IntroTheme(content=content['themes']['IntroTheme']),
        character=craeteCharacterJson(content['character']),
        content=content['dialogContext']
    )

    engineer_dialog.handle_message('Привет, Я HR Из компании Google. Я пишу Вам чтобы предложить работу. Давайте обсудим вашу работу')
