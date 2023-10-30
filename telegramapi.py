import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

def load_api_key():
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv("TELEGRAM_BOT_API_KEY")


app = ApplicationBuilder().token(load_api_key()).build()

app.add_handler(CommandHandler("hello", hello))

app.run_polling()