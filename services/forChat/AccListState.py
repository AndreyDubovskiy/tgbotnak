import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError, UserDeletedError, UserInvalidError, UserDeactivatedError, UsernameInvalidError

class AccListState(UserState):
    async def start_msg(self):
        self.edit = None
        self.acc_count = 0
        self.list_acc_info = []
        self.current_session_name = None
        self.current_session = None
        return Response(text="Список акаунтів ("+str(self.acc_count)+"): ", buttons=markups.generate_cancel())

    async def next_msg(self, message: str):
        if self.edit == "add_acc":
            lines = message.split("\n")
            for tmp in lines:
                acc_info = tmp.split(":")
                if len(acc_info) < 2:
                    self.list_acc_info = []
                    return Response("Ви ввели замало інформації про акаунт! спробуйте ще раз!", buttons=markups.generate_cancel())
                elif len(acc_info) == 2:
                    self.list_acc_info.append({"name": acc_info[0],
                                               "phone": acc_info[1]})
                elif len(acc_info) == 3:
                    self.list_acc_info.append({"name": acc_info[0],
                                               "phone": acc_info[1],
                                               "password": acc_info[2]})
                elif len(acc_info) == 5:
                    self.list_acc_info.append({"name": acc_info[0],
                                               "phone": acc_info[1],
                                               "password": acc_info[2],
                                               "api_id": acc_info[3],
                                               "api_hash": acc_info[4]})
                else:
                    self.list_acc_info = []
                    return Response("Ви ввели забагато інформації про акаунт! спробуйте ще раз!",
                                    buttons=markups.generate_cancel())
            self.edit = "code_acc"
            return Response("Введіть код, який надіслали у форматі 1-2-3-4-5\n("+self.list_acc_info[0]["phone"]+")", buttons=markups.generate_cancel())
        elif self.edit == "code_acc":
            if self.list_acc_info[0].get("api_id", None):
                pass
            elif self.list_acc_info[0].get("password", None):
                pass
            else:
                pass


    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            return Response(redirect="/menu")
        elif data_btn == "/add":
            self.edit = "add_acc"
            return Response("Напишіть дані акаунту у такому форматі:\n"
                            "назва(для себе):телефон:пароль(якщо є):api id(якшо є):api hash(якщо є)\n"
                            "Наприклад: у нас є тільки пароль та телефон\n"
                            "акаунт1:+380661231212:сосиска123\n"
                            "Вводити можна зразу декілька акаунтів, де кожний з нового рядку", buttons=markups.generate_cancel())
