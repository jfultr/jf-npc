import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from package.travel_agent import TravelAgent

def load_api_key(name):
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv(name)

travel_agent = TravelAgent()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, 
        text=travel_agent.greeting)
    
async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = await travel_agent.handle_user_message(update.message.text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


if __name__ == '__main__':
    telegram_token = load_api_key("TELEGRAM_BOT_API_KEY")
    application = ApplicationBuilder().token(telegram_token).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), talk)


    application.add_handler(start_handler)
    application.add_handler(echo_handler)


    application.run_polling()