from telebot.async_telebot import AsyncTeleBot
from telebot import types
from services.forChat.UserState import UserState
from services.forChat.StartState import StartState
from services.forChat.LogState import LogState
from services.forChat.MenuState import MenuState
from services.forChat.PostState import PostState
from services.forChat.LinkState import LinkState
from services.forChat.ChangeAdminState import ChangeAdminState
from services.forChat.ChangeStartState import ChangeStartState

class BuilderState:
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    def create_state(self, data_txt: str, user_id: str, user_chat_id: str, bot: AsyncTeleBot, user_name: str = None) -> UserState:
        clssses = {
            "/start": StartState,
            "/menu": MenuState,
            "/postlist": PostState,
            "/log": LogState,
            "/links": LinkState,
            "/passwordadmin": ChangeAdminState,
            "/change_start_text": ChangeStartState,
        }
        return clssses[data_txt](user_id, user_chat_id, bot, user_name)