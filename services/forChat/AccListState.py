import os

import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError, UserDeletedError, UserInvalidError, UserDeactivatedError, UsernameInvalidError

from db.controllers.AccsController import AccsController
from db.controllers.ProxysController import ProxysController


class AccListState(UserState):
    async def start_msg(self):

        self.path_sessions = "saved/sessions/"

        self.accs_controller = AccsController()
        self.proxy_controller = ProxysController()

        self.edit = None
        self.acc_count = len(self.accs_controller.get_by(is_active=True))
        self.list_acc_info = []
        self.current_session_name = None
        self.current_session = None
        self.current_proxy = None
        self.current_acc_model = None

        self.current_phone = None

        self.offset = 0
        self.limit = 10

        self.need_page_buttons = False
        if self.acc_count > self.limit:
            self.need_page_buttons = True

        return Response(text="Список акаунтів ("+str(self.acc_count)+"): ",
                        buttons=markups.generate_list_acc(self.accs_controller.get_by(is_active=True, limit=self.limit, offset=self.offset), page=self.need_page_buttons))

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
            await self.send_code()
            return Response("Введіть код, який надіслали у форматі 1-2-3-4-5\n("+self.list_acc_info[0]["phone"]+")", buttons=markups.generate_cancel())

        elif self.edit == "code_acc":
            code = message.replace(".", "").replace(" ", "").replace("-", "")
            try:
                await self.current_session.sign_in(self.current_acc_model.phone, code)
            except SessionPasswordNeededError:
                await self.current_session.sign_in(password=self.current_acc_model.password)
            except Exception as ex:
                return Response("Сталася помилка!\n\n"+str(ex), redirect="/menu")
            finally:
                tmp_bool = await self.current_session.is_user_authorized()
                print("ADD is_user_authorized", tmp_bool)
                if (tmp_bool):
                    self.current_acc_model.is_active = True
                    self.current_acc_model = self.accs_controller.save(self.current_acc_model)
                    self.list_acc_info.pop(0)
                    await self.current_session.disconnect()
                    if len(self.list_acc_info) > 0:
                        await self.send_code()
                        return Response("Прийнято!\n\nВведіть код, який надіслали у форматі 1-2-3-4-5\n("+self.list_acc_info[0]["phone"]+")", buttons=markups.generate_cancel())
                    else:
                        return Response(redirect="/menu")
                else:
                    return Response("Код було введено невірно! Спробуйте ще раз:", buttons=markups.generate_cancel())



    async def get_proxy(self):
        proxys = self.proxy_controller.get_sorted_by_accs_count()
        print("LEN PROXY", len(proxys))
        if len(proxys) == 0:
            return None
        else:
            print("PROXY_id", proxys[-1].id)
            print("PROXY_ip", proxys[-1].ip)
            print("PROXY_port", proxys[-1].port)
            return proxys[-1]
    async def send_code(self):
        if self.list_acc_info[0].get("api_id", None):
            proxy = await self.get_proxy()
            if proxy != None:
                proxy = proxy.id
            else:
                proxy = None
            print("PROXY SET", proxy)
            acc_model = self.accs_controller.create(name=self.list_acc_info[0]['name'],
                                                    session_name="asd",
                                                    api_id=self.list_acc_info[0]['api_id'],
                                                    api_hash=self.list_acc_info[0]['api_hash'],
                                                    phone=self.list_acc_info[0]['phone'],
                                                    password=self.list_acc_info[0]['password'],
                                                    proxy_id=proxy)
            acc_model.session_name = str(acc_model.id)
            acc_model = self.accs_controller.save(acc_model)

            if proxy:
                print("start1")
                self.current_proxy = self.proxy_controller.get_by(id=proxy)[0]
                proxy = (
                          self.current_proxy.type_proxy,
                          self.current_proxy.ip,
                          self.current_proxy.port,
                          True,
                          self.current_proxy.login,
                          self.current_proxy.password
                      )
                self.current_session_name = acc_model.session_name
                self.current_session = TelegramClient(session=self.path_sessions+acc_model.session_name,
                                                      api_id=acc_model.api_id,
                                                      api_hash=acc_model.api_hash,
                                                      proxy=proxy
                                                      )
            else:
                self.current_proxy = None
                self.current_session_name = acc_model.session_name
                self.current_session = TelegramClient(session=self.path_sessions+acc_model.session_name,
                                                      api_id=acc_model.api_id,
                                                      api_hash=acc_model.api_hash
                                                      )
            self.current_acc_model = acc_model
            await self.current_session.connect()
            await self.current_session.send_code_request(phone=self.current_acc_model.phone)
        elif self.list_acc_info[0].get("password", None):
            proxy = await self.get_proxy()
            if proxy != None:
                proxy = proxy.id
            else:
                proxy = None
            acc_model = self.accs_controller.create(name=self.list_acc_info[0]['name'],
                                                    session_name="asd",
                                                    phone=self.list_acc_info[0]['phone'],
                                                    password=self.list_acc_info[0]['password'],
                                                    proxy_id=proxy)
            acc_model.session_name = str(acc_model.id)
            acc_model = self.accs_controller.save(acc_model)

            if proxy:
                print("start2")
                self.current_proxy = self.proxy_controller.get_by(id=proxy)[0]
                proxy = (
                    self.current_proxy.type_proxy,
                    self.current_proxy.ip,
                    self.current_proxy.port,
                    True,
                    self.current_proxy.login,
                    self.current_proxy.password
                )
                self.current_session_name = acc_model.session_name
                self.current_session = TelegramClient(session=self.path_sessions+acc_model.session_name,
                                                      api_id=acc_model.api_id,
                                                      api_hash=acc_model.api_hash,
                                                      proxy=proxy
                                                      )
            else:
                self.current_proxy = None
                self.current_session_name = acc_model.session_name
                self.current_session = TelegramClient(session=self.path_sessions+acc_model.session_name,
                                                      api_id=acc_model.api_id,
                                                      api_hash=acc_model.api_hash
                                                      )
            self.current_acc_model = acc_model
            await self.current_session.connect()
            await self.current_session.send_code_request(phone=self.current_acc_model.phone)
        else:
            proxy = await self.get_proxy()
            if proxy != None:
                proxy = proxy.id
            else:
                proxy = None
            acc_model = self.accs_controller.create(name=self.list_acc_info[0]['name'],
                                                    session_name="asd",
                                                    phone=self.list_acc_info[0]['phone'],
                                                    proxy_id=proxy)
            acc_model.session_name = str(acc_model.id)
            acc_model = self.accs_controller.save(acc_model)

            if proxy:
                print("start3")
                self.current_proxy = self.proxy_controller.get_by(id=proxy)[0]
                proxy = (
                    self.current_proxy.type_proxy,
                    self.current_proxy.ip,
                    self.current_proxy.port,
                    True,
                    self.current_proxy.login,
                    self.current_proxy.password
                )
                self.current_session_name = acc_model.session_name
                self.current_session = TelegramClient(session=self.path_sessions+acc_model.session_name,
                                                      api_id=acc_model.api_id,
                                                      api_hash=acc_model.api_hash,
                                                      proxy=proxy
                                                      )
                print("pr", proxy)
            else:
                self.current_proxy = None
                self.current_session_name = acc_model.session_name
                self.current_session = TelegramClient(session=self.path_sessions+acc_model.session_name,
                                                      api_id=acc_model.api_id,
                                                      api_hash=acc_model.api_hash
                                                      )
            self.current_acc_model = acc_model
            await self.current_session.connect()
            await self.current_session.send_code_request(phone=self.current_acc_model.phone)

    async def get_phones(self):
        accs = self.accs_controller.get_by(is_active=True)
        phones = []
        for i in accs:
            phones.append(i.phone)
        return phones

    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            if self.current_phone:
                return Response(redirect="/accs")
            return Response(redirect="/menu")
        elif data_btn == "/next":
            self.offset += self.limit
            tmp = self.accs_controller.get_by(is_active=True, limit=self.limit, offset=self.offset)
            if len(tmp) == 0:
                self.offset -= self.limit
            return Response(text="Список акаунтів (" + str(self.acc_count) + "): ",
                            buttons=markups.generate_list_acc(
                                self.accs_controller.get_by(is_active=True, limit=self.limit, offset=self.offset),
                                page=self.need_page_buttons))
        elif data_btn == "/back":
            if self.offset == 0:
                return Response(text="Список акаунтів (" + str(self.acc_count) + "): ",
                                buttons=markups.generate_list_acc(
                                    self.accs_controller.get_by(is_active=True, limit=self.limit, offset=self.offset),
                                    page=self.need_page_buttons))
            else:
                self.offset -= self.limit
                return Response(text="Список акаунтів (" + str(self.acc_count) + "): ",
                                buttons=markups.generate_list_acc(
                                    self.accs_controller.get_by(is_active=True, limit=self.limit, offset=self.offset),
                                    page=self.need_page_buttons))
        elif data_btn == "/add":
            self.edit = "add_acc"
            return Response("Напишіть дані акаунту у такому форматі:\n"
                            "назва(для себе):телефон:пароль(якщо є):api id(якшо є):api hash(якщо є)\n"
                            "Наприклад: у нас є тільки пароль та телефон\n"
                            "акаунт1:+380661231212:сосиска123\n"
                            "Вводити можна зразу декілька акаунтів, де кожний з нового рядку", buttons=markups.generate_cancel())
        elif data_btn == "/delete":

            self.current_acc_model = self.accs_controller.get_by(phone=self.current_phone)[0]
            name_session = self.current_acc_model.session_name
            self.accs_controller.delete(id=self.current_acc_model.id)
            try:
                os.remove(f"saved/sessions/{name_session}.session")
            except:
                pass
            return Response("Видалено!", redirect="/accs")
        elif data_btn in (await self.get_phones()):
            self.current_phone = data_btn
            self.current_acc_model = self.accs_controller.get_by(phone=self.current_phone)[0]
            if self.current_acc_model.proxy:
                return Response(f"Назва: {self.current_acc_model.name}\n"
                                f"Телефон: {self.current_acc_model.phone}\n"
                                f"Пароль: {self.current_acc_model.password}\n"
                                f"Проксі: {self.current_acc_model.proxy.ip+':'+str(self.current_acc_model.proxy.port)}",
                                buttons=markups.generate_delete_cancel())
            else:
                return Response(f"Назва: {self.current_acc_model.name}\n"
                                f"Телефон: {self.current_acc_model.phone}\n"
                                f"Пароль: {self.current_acc_model.password}\n"
                                f"Проксі: None",
                                buttons=markups.generate_delete_cancel())

