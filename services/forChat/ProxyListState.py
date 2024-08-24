import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response

from db.controllers.AccsController import AccsController
from db.controllers.ProxysController import ProxysController, ProxyModel


class ProxyListState(UserState):
    async def start_msg(self):
        self.MAX_ON_PAGE = 10

        self.accs_controller = AccsController()
        self.proxy_controller = ProxysController()

        self.edit = None

        self.offset = 0
        self.limit = self.MAX_ON_PAGE

        self.proxys = self.proxy_controller.get_all()
        self.current_proxy: ProxyModel  = None

        self.need_page_buttons = False
        if len(self.proxys) > self.limit:
            self.need_page_buttons = True

        return Response(text="Список проксі ("+str(len(self.proxys))+"): ",
                        buttons=markups.generate_list_proxy(self.proxy_controller.get_by(
                                                                                        limit=self.limit,
                                                                                        offset=self.offset),
                                                          page=self.need_page_buttons))

    def int_to_type_proxy(self, type_id):
        res = None
        if type_id == 1:
            res = "socks4"
        elif type_id == 2:
            res = "socks5"
        elif type_id == 3:
            res = "http"
        return res
    async def next_msg(self, message: str):
        if self.edit == "add_proxy":
            count_add = 0
            error_proxys = []
            proxy_texts = message.split("\n")
            for i in proxy_texts:
                splited_i = i.split(":")
                if len(splited_i) != 5:
                    error_proxys.append(i)
                    continue
                type_proxy = None
                if splited_i[0].lower() == 'socks4':
                    type_proxy = 1
                elif splited_i[0].lower() == 'socks5':
                    type_proxy = 2
                elif splited_i[0].lower() == 'http':
                    type_proxy = 3
                if type_proxy == None:
                    error_proxys.append(i)
                    continue
                ip_proxy = splited_i[1]
                try:
                    port_proxy = int(splited_i[2])
                except:
                    error_proxys.append(i)
                    continue
                login_proxy = splited_i[3]
                pass_proxy = splited_i[4]

                tmp = self.proxy_controller.get_by(ip=ip_proxy, port=port_proxy)
                if len(tmp) != 0:
                    error_proxys.append(i)
                    continue

                self.proxy_controller.create(type_proxy=type_proxy,
                                             ip=ip_proxy,
                                             port=port_proxy,
                                             login=login_proxy,
                                             password=pass_proxy)
                count_add += 1
            text_add = ""
            if len(error_proxys) > 0:
                text_add = (f"Помилки у записі {len(error_proxys)} проксі або ж вони повторюються:\n")
                for y in error_proxys:
                    text_add += f"❗️ {y}\n"
                text_add += "\nСпробуйте ще раз!"
            return Response(text=f"Додано {count_add} проксі!\n"+text_add,
                            redirect="/proxys")

    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            if self.current_proxy:
                return Response(redirect="/proxys")
            return Response(redirect="/menu")
        elif data_btn == "/next":
            self.offset += self.limit
            tmp = self.proxy_controller.get_by(limit=self.limit, offset=self.offset)
            if len(tmp) == 0:
                self.offset -= self.limit
            return Response(text="Список проксі (" + str(len(self.proxys)) + "): ",
                            buttons=markups.generate_list_proxy(
                                self.proxy_controller.get_by(limit=self.limit, offset=self.offset),
                                page=self.need_page_buttons))
        elif data_btn == "/back":
            if self.offset == 0:
                return Response(text="Список проксі (" + str(len(self.proxys)) + "): ",
                                buttons=markups.generate_list_proxy(
                                    self.proxy_controller.get_by(limit=self.limit, offset=self.offset),
                                    page=self.need_page_buttons))
            else:
                self.offset -= self.limit
                return Response(text="Список проксі (" + str(len(self.proxys)) + "): ",
                                buttons=markups.generate_list_proxy(
                                    self.proxy_controller.get_by(limit=self.limit, offset=self.offset),
                                    page=self.need_page_buttons))
        elif data_btn == "/add":
            self.edit = "add_proxy"
            return Response("Напишіть дані проксі у такому форматі:\n"
                            "тип проксі:ip:порт:логін:пароль\n"
                            "Наприклад:\n"
                            "http:127.0.0.1:8080:login:pass123\n"
                            "Вводити можна зразу декілька проксі, де кожний з нового рядку", buttons=markups.generate_cancel())
        elif data_btn == "/delete":
            if self.current_proxy != None:
                self.proxy_controller.delete(id=self.current_proxy.id)
                return Response("Видалено!", redirect="/proxys")
        else:
            try:
                id_proxy = int(data_btn)
                self.current_proxy = self.proxy_controller.get_by(id=id_proxy)[0]
                return Response(text=f"[Проксі]\n"
                                     f"Тип: {self.int_to_type_proxy(self.current_proxy.type_proxy)}\n"
                                     f"Айпі: {self.current_proxy.ip}\n"
                                     f"Порт: {self.current_proxy.port}\n"
                                     f"Логін: {self.current_proxy.login}\n"
                                     f"Пароль: {self.current_proxy.password}",
                                buttons=markups.generate_proxy())
            except:
                return Response(redirect="/menu")


