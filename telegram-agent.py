from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from internal.adapter import get_travel_agent
from package.common import read_api_key
from package.database import is_chat_stored


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_chat_stored(str(update.effective_chat.id)):
        greeting = get_travel_agent(
            update.effective_chat.id,
            update.effective_user.id).handle_start()
        await context.bot.send_message(chat_id=update.effective_chat.id, 
            text=greeting)
    else:
        return


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_chat_stored(str(update.effective_chat.id)):
        travel_agent = get_travel_agent(
            update.effective_chat.id,
            update.effective_user.id)
        response = await travel_agent.a_handle_message(update.message.text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    else:
        return


def app():  
    # bot 
    telegram_token = read_api_key("TELEGRAM_BOT_API_KEY")
    application = ApplicationBuilder().token(telegram_token).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), talk)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.run_polling()

if __name__ == '__main__':
    app()