import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# gpt powered
from openai import OpenAI


def load_api_key(name):
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv(name)


# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

_greeting_text = "Привет! Я помогу вам организовать ваше путешествие.\n" \
        "Давайте начнем с вашего возраста. Сколько вам лет?"

# Функция-обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, 
        text=_greeting_text)

# get_age
# get_city_from
# get_city_to
# get_people_count
# cancel
# error

_starting_context = "Ты онлайн турестический агент.\n" \
                    "Тебе необходимо узнать у клиента: возраст, пункт отправления, пункт прибытия, количество людей.\n" \
                    "Задавай вопросы пока не узнаешь ответы на все вопросы. По мере заполняй профайл клиента\n"

_messages = [
    {
        "role": "system",
        "content": _starting_context
    },
    {
        "role": "assistant",
        "content": _greeting_text
    }
]

async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _messages.append(
        {
            "role": "user",
            "content": update.message.text
        }
    )
    comp = client.chat.completions.create(
        messages=_messages,
        model="gpt-3.5-turbo",
    )
    gpt_response = comp.choices[0].message.content
    print(gpt_response)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=gpt_response)

    comp = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": \
                    f"вопрос: {_messages[-2]['content']}"
                    f"ответ: {update.message.text}\n" \
                    "Прочитай эти сообщения и заполни эти поля. Оставляй поля пустыми, если данные не указаны\n" \
                    "Возраст: <int>\n" \
                    "Пункт отправления: <string>\n" \
                    "Пункт прибытия: <string>\n" \
                    "Количество людей: <int>\n" \
            }
        ],
        model="gpt-3.5-turbo",
    )

    _messages.append(
        {
            "role": "assistant",
            "content": gpt_response
        }
    )
    gpt_response = comp.choices[0].message.content
    print(gpt_response)


if __name__ == '__main__':
    openai_token = load_api_key("OPENAI_API_KEY")
    telegram_token = load_api_key("TELEGRAM_BOT_API_KEY")

    client = OpenAI(
        # This is the default and can be omitted
        api_key=openai_token
    )
    application = ApplicationBuilder().token(telegram_token).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), talk)


    application.add_handler(start_handler)
    application.add_handler(echo_handler)


    application.run_polling()