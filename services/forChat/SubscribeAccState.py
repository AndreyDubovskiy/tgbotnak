import asyncio
import random

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
        self.logger.filename = self.__class__.__name__
        self.logger.autosave = True

        self.RANGE_COOLDOWN = 20 # in proc
        self.cooldown = 5

        self.accs_controller = AccsController()
        self.event_controller = EventsController()

        self.count_acc = len(self.accs_controller.get_by(is_active=True))

        self.edit = "url"
        self.current_url = None
        self.count_in_url_accs = 0

        self.need_count =  None

        self.message_edit = None

        self.is_private = False

        return Response(text=f"Акаунтів у наявності: {self.count_acc}\n"
                             f"(Посилання на приватний канал з заявками не підтримується)\n"
                             f"Уведіть посилання на групу чи канал: ",
                        buttons=markups.generate_cancel())

    async def next_msg(self, message: str):
        if self.edit == "url":
            self.current_url = message
            self.count_in_url_accs = self.count_acc - len(self.event_controller.get_by(name_type="join_"+self.current_url))
            self.edit = "count"
            return Response(text=f"Для даного каналу для вступу є {self.count_in_url_accs} акаунтів.\n"
                                 f"Уведіть скільки вам потрібно підписок та через пробіл якщо потрібно затримку у секундах:",
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
            return Response(async_end=True, redirect="/menu")


    async def async_work(self):
        await self.work()

    async def work(self):

        current_count = 0
        error_count = 0
        msg = await self.bot.send_message(chat_id=self.user_chat_id,
                                          text=f"[Статус Підписки]\n"
                                               f"[{self.current_url}]\n"
                                               f"Готово: {current_count} з {self.need_count}\n"
                                               f"Помилок: {error_count}")
        accs = self.accs_controller.get_by(is_active=True)
        self.logger.log("WORK", f"start work", f"accs_len {len(self.accs)}")
        for i in accs:
            try:
                tmp_session: TelegramClient = await session_list.get_session(i.phone)
            except Exception as ex:
                self.logger.log("ERROR", i.phone, ex)
                continue
            try:
                tmp = self.event_controller.get_by(name_type="join_"+self.current_url,
                                                   acc_id=i.id)
                if len(tmp) > 0:
                    continue
                self.logger.log("WORK", "is_connected", tmp_session.is_connected())
                self.logger.log("WORK", "is_user_authorized", await tmp_session.is_user_authorized())
                self.logger.log("WORK", "start", self.current_url)
                if self.is_private == False:
                    await tmp_session(JoinChannelRequest(self.current_url))
                    entity = await tmp_session.get_entity(self.current_url.split("/")[-1])
                    self.logger.log("WORK", i.phone, "chanellEntity", entity)
                    current_count += 1
                    self.logger.log("WORK", i.phone, "COUNT++")
                    self.event_controller.create(acc_id=i.id,
                                                 name_type="join_"+self.current_url,
                                                 tg_id = str(entity.id),
                                                 tg_id_group=str(entity.id))
                    await self.bot.edit_message_text(text=f"[Статус Підписки]\n"
                                                   f"[{self.current_url}]\n"
                                                   f"Готово: {current_count} з {self.need_count}\n"
                                                   f"Помилок: {error_count}",
                                                     chat_id=self.user_chat_id,
                                                     message_id=msg.id)
                    if current_count >= self.need_count:
                        break
                    else:
                        await asyncio.sleep(random.uniform((self.cooldown*(1.0-(self.RANGE_COOLDOWN/100))),
                                                           ((self.cooldown*(1.0+(self.RANGE_COOLDOWN/100))))))
                else:
                    try:
                        invite_code: str = self.current_url.split("/")[-1].replace("+", "")
                        self.logger.log("WORK", i.phone, "INVITE", invite_code)
                        await tmp_session(ImportChatInviteRequest(invite_code))
                        entity = await tmp_session(CheckChatInviteRequest(invite_code))
                        self.logger.log("WORK", i.phone, "TYPOENTYTY", entity)
                        current_count += 1
                        self.logger.log("WORK", i.phone, "COUNT++")
                        self.is_private = True
                        self.event_controller.create(acc_id=i.id,
                                                     name_type="join_" + self.current_url,
                                                     tg_id=str(entity.chat.id),
                                                     tg_id_group=str(entity.chat.id))
                        await self.bot.edit_message_text(text=f"[Статус Підписки]\n"
                                                              f"[{self.current_url}]\n"
                                                              f"Готово: {current_count} з {self.need_count}\n"
                                                              f"Помилок: {error_count}",
                                                         chat_id=self.user_chat_id,
                                                         message_id=msg.id)
                    except Exception as ex:
                        error_count += 1
                        self.logger.log("ERROR", i.phone, ex)
            except ValueError:
                try:
                    invite_code: str = self.current_url.split("/")[-1].replace("+", "")
                    self.logger.log("WORK", i.phone, "INVITE", invite_code)
                    await tmp_session(ImportChatInviteRequest(invite_code))
                    entity = await tmp_session(CheckChatInviteRequest(invite_code))
                    self.logger.log("WORK", i.phone, "TYPOENTYTY", entity)
                    current_count +=1
                    self.logger.log("WORK", i.phone, "COUNT++")
                    self.is_private = True
                    self.event_controller.create(acc_id=i.id,
                                                 name_type="join_" + self.current_url,
                                                 tg_id=str(entity.chat.id),
                                                 tg_id_group=str(entity.chat.id))
                    await self.bot.edit_message_text(text=f"[Статус Підписки]\n"
                                               f"[{self.current_url}]\n"
                                               f"Готово: {current_count} з {self.need_count}\n"
                                               f"Помилок: {error_count}",
                                                     chat_id=self.user_chat_id,
                                                     message_id=msg.id)
                except Exception as ex:
                    error_count +=  1
                    self.logger.log("ERROR", i.phone, ex)
            except Exception as ex:
                error_count += 1
                self.logger.log("ERROR", i.phone, ex)
            finally:
                await session_list.give_away_session(i.phone)
                self.logger.log("END", "END")
        await self.bot.edit_message_text(text=f"[Статус Підписки]\n"
                                               f"[{self.current_url}]\n"
                                              f"[Закінчено]\n"
                                               f"Готово: {current_count} з {self.need_count}\n"
                                               f"Помилок: {error_count}",
                                         chat_id=self.user_chat_id,
                                         message_id=msg.id)




    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            return Response(redirect="/menu")