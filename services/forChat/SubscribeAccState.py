import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller

from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import CheckChatInviteRequest, ImportChatInviteRequest

from db.controllers.AccsController import AccsController
from db.controllers.EventsController import EventsController

from services.AccSessionList import session_list

class SubscribeAccState(UserState):
    async def start_msg(self):
        self.accs_controller = AccsController()
        self.event_controller = EventsController()

        self.count_acc = len(self.accs_controller.get_by(is_active=True))

        self.edit = "url"
        self.current_url = None
        self.count_in_url_accs = 0

        self.need_count =  None

        self.message_edit = None

        return Response(text=f"Акаунтів у наявності: {self.count_acc}\n"
                             f"Уведіть посилання на групу чи канал: ",
                        buttons=markups.generate_cancel())

    async def next_msg(self, message: str):
        if self.edit == "url":
            self.current_url = message
            self.count_in_url_accs = self.count_acc - len(self.event_controller.get_by(name_type="join_"+self.current_url))
            self.edit = "count"
            return Response(text=f"Для даного каналу для вступу є {self.count_in_url_accs} акаунтів.\n"
                                 f"Уведіть скільки вам потрібно підписок:",
                            buttons=markups.generate_cancel())
        elif self.edit == "count":
            try:
                self.need_count = int(message)
                if self.need_count <= 0 or self.need_count > self.count_in_url_accs:
                    raise Exception("Error, too much")
            except:
                return Response(text=f"Помилка!\n"
                                     f"Ви впевненні, що ввели все коректно?\n"
                                     f"Спробуйте ще раз:",
                                buttons=markups.generate_cancel())
            await self.work()
            return Response(
                text=f"Закінчено!",
                redirect="/menu")

    async def work(self):
        current_count = 0
        msg = await self.bot.send_message(chat_id=self.user_chat_id,
                                          text=f"[Статус]\n"
                                               f"{current_count} з {self.need_count}")
        accs = self.accs_controller.get_by(is_active=True)
        for i in accs:
            tmp = self.event_controller.get_by(name_type="join_"+self.current_url,
                                               acc_id=i.id)
            if len(tmp) > 0:
                continue
            try:
                tmp_session: TelegramClient = await session_list.get_session(i.phone)
            except:
                continue
            print("is_connected", tmp_session.is_connected())
            print("is_user_authorized", await tmp_session.is_user_authorized())
            print("start", self.current_url)
            await tmp_session(JoinChannelRequest(self.current_url))
            entity = await tmp_session.get_entity(self.current_url.split("/")[-1])
            print(entity)
            current_count += 1
            self.event_controller.create(acc_id=i.id,
                                         name_type="join_"+self.current_url,
                                         tg_id = str(entity.id),
                                         tg_id_group=str(entity.id))
            await self.bot.edit_message_text(text=f"[Статус]\n"
                                               f"{current_count} з {self.need_count}",
                                             chat_id=self.user_chat_id,
                                             message_id=msg.id)
            await session_list.give_away_session(i.phone)
            if current_count >= self.need_count:
                break




    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            return Response(redirect="/menu")