from telebot.async_telebot import AsyncTeleBot
from telebot import types
from services.forChat.UserState import UserState
from services.forChat.LogState import LogState
from services.forChat.MenuState import MenuState
from services.forChat.ChangeAdminState import ChangeAdminState
from services.forChat.AccListState import AccListState
from services.forChat.SubscribeAccState import SubscribeAccState
from services.forChat.ViewState import ViewState
from services.forChat.ReactionState import ReactionState
from services.forChat.WordsListState import WordsListState
from services.forChat.CommentState import CommentState
from services.forChat.ProxyListState import ProxyListState

class BuilderState:
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    def create_state(self, data_txt: str, user_id: str, user_chat_id: str, bot: AsyncTeleBot, user_name: str = None, message: types.Message = None) -> UserState:
        clssses = {
            "/menu": MenuState,
            "/log": LogState,
            "/passwordadmin": ChangeAdminState,
            "/accs": AccListState,
            "/sub": SubscribeAccState,
            "/view": ViewState,
            "/reaction": ReactionState,
            "/groups": WordsListState,
            "/comment": CommentState,
            "/proxys": ProxyListState,
        }
        return clssses[data_txt](user_id, user_chat_id, bot, user_name, message)