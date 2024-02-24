from __future__ import annotations

from npc.npc import NPC
from npc.cyber_travel_agent import CyberTravelAgent

# design files
from internal.messagelist import MessageList
from internal.profile import Profile
from internal.documentation import QAfile
from internal.question_classification import get_question_classificator

# agents cache
agents = {}


def get_travel_agent(chat_id: int, user_id: int) -> TelegramAdapter:
    if chat_id in agents:
        return agents[chat_id]
    else:
        npc = CyberTravelAgent(
            MessageList(str(chat_id)),
            Profile(str(user_id))
        )
        bot = TelegramAdapter(npc)
        agents.update({chat_id: bot})
        return bot


class TelegramAdapter:
    def __init__(self, npc: NPC) -> None:
        self._npc = npc

    def handle_start(self):
        return self._npc.greet("")
    
    async def a_handle_start(self):
        return await self._npc.a_greet("")
    
    def handle_message(self, message):
        return self._npc.talk(message)

    async def a_handle_message(self, message):
        return await self._npc.a_talk(message)
