from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from internal.travel_agent import TravelAgent, greeting
from package.common import read_api_key


agents = {}

"""
"chats": {
    "chat_id": int
    "profile": {}
    "messages": [
        {
            role: str
            content: str
        },
        ...
    ]
},
...
    
"""
def is_agent_in_memmory(agent):
    pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in agents:
        return
    else:
        agents.update({update.effective_chat.id: TravelAgent(update.effective_chat.id)})
        await context.bot.send_message(chat_id=update.effective_chat.id, 
            text=greeting)
    

async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.id in agents:
        return
    else:
        travel_agent = agents[update.effective_chat.id]
    response = await travel_agent.handle_user_message(update.message.text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


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