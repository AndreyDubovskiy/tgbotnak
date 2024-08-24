import asyncio
import random

import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller

from telethon import TelegramClient
from telethon import types
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import CheckChatInviteRequest, ImportChatInviteRequest, GetMessagesViewsRequest
from telethon.tl.functions.messages import SendReactionRequest


from db.controllers.AccsController import AccsController
from db.controllers.EventsController import EventsController
from db.controllers.GroupwordssController import GroupwordssController
from db.controllers.GroupwordssController import GroupwordsModel

from services.AccSessionList import session_list

from datetime import datetime, timedelta

class CommentState(UserState):
    async def start_msg(self):
        self.acc_controller = AccsController()
        self.events_controller = EventsController()
        self.group_controller = GroupwordssController()

        self.MAX_ON_PAGE = 10
        self.COOLDOWN = 2
        self.RANGE_COOLDOWN = 10

        self.group_id = None
        self.post_id = None

        self.group_comments: GroupwordsModel = None

        self.current_page = 0
        self.page_bool = False

        self.groups = self.group_controller.get_all()
        if len(self.groups) > self.MAX_ON_PAGE:
            self.page_bool = True


        self.edit = "post"
        return Response(text="Перишліть сюди пост який потрібно продивитись:")

    async def next_msg(self, message: str):
        if self.edit == "post":
            self.group_id = str(self.message_obj.forward_from_chat.id)
            print("Forvard chanell ", self.group_id)
            self.post_id = str(self.message_obj.forward_from_message_id)
            print("Post ", self.post_id)
            self.edit = "count"
            self.accs = self.events_controller.get_by(tg_id=self.group_id.replace("-100", ""), name_type_value="join_")
            return Response(text=f"Доступно для цього поста {len(self.accs)} акаунтів\nНапишіть кількість коментарів та затримку (якщо потрібно) через пробіл:")
        elif self.edit == "count":
            try:
                if message.count(" ") == 0:
                        self.count = int(message)
                elif message.count(" ") == 1:
                    self.count = int(message.split(" ")[0])
                    self.COOLDOWN = float(message.split(" ")[1])
                else:
                    return Response("Ви впевнені що ввели все коректно? Спробуйте ще раз:")
                self.edit = "group"
                return Response("Виберіть групу коментарів:",
                                    buttons=markups.generate_list_groupswords(
                                            arr=self.group_controller.get_by(offset=self.current_page * self.MAX_ON_PAGE,
                                                                             limit=self.MAX_ON_PAGE),
                                            page=self.page_bool,
                                            add=False
                                    )
                                )
            except:
                return Response("Ви впевнені що ввели все коректно? Спробуйте ще раз:")


    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            return Response(redirect="/menu")
        elif data_btn == "/next":
            self.current_page += 1
            tmp = self.group_controller.get_by(offset=self.current_page * self.MAX_ON_PAGE, limit=self.MAX_ON_PAGE)
            if len(tmp) == 0:
                self.current_page -= 1
            return Response("Виберіть групу коментарів:",
                                    buttons=markups.generate_list_groupswords(
                                            arr=self.group_controller.get_by(offset=self.current_page * self.MAX_ON_PAGE,
                                                                             limit=self.MAX_ON_PAGE),
                                            page=self.page_bool,
                                            add=False
                                    )
                                )
        elif data_btn == "/back":
            if self.current_page > 0:
                self.current_page -= 1
            return Response("Виберіть групу коментарів:",
                            buttons=markups.generate_list_groupswords(
                                arr=self.group_controller.get_by(offset=self.current_page * self.MAX_ON_PAGE,
                                                                 limit=self.MAX_ON_PAGE),
                                page=self.page_bool,
                                add=False
                            )
                            )
        elif self.edit == "group":
            id_group = int(data_btn)
            self.group_comments = self.group_controller.get_by(id=id_group)[0]
            return Response(redirect="/menu", async_end=True)

            

    async def async_work(self):
        count = 0
        error_count = 0

        now = datetime.now()
        now = now - timedelta(hours=12)

        msg = await self.bot.send_message(chat_id=self.user_chat_id,
                                          text=f"[Статус Коментарі]\n"
                                               f"[{self.group_id}]\n"
                                               f"Готово: {count} з {self.count}\n"
                                               f"Помилок: {error_count}")

        for i in self.accs:
            try:
                ttt = self.events_controller.get_by(acc_id=i.acc_id,
                                                    name_type_value=f"Comment",
                                                    tg_id=self.group_id.replace("-100", ""),
                                                    tg_id_group=self.post_id,
                                                    )
                if len(ttt) != 0:
                    continue

                acc = self.acc_controller.get_by(id=i.acc_id)[0]
                try:
                    ses: TelegramClient = await session_list.get_session(acc.phone)
                except:
                    error_count += 1
                    continue
            except:
                error_count += 1
                continue
            try:

                chanell_entity = await ses.get_entity(int(self.group_id.replace("-100", "")))
                print("chanellEntity", chanell_entity)

                text = random.choice(self.group_comments.words)

                await ses.send_message(
                    entity=chanell_entity,
                    message=text.name,
                    comment_to=int(self.post_id)
                )

                count+=1
                await self.bot.edit_message_text(text=f"[Статус Коментарі]\n"
                                               f"[{self.group_id}]\n"
                                               f"Готово: {count} з {self.count}\n"
                                               f"Помилок: {error_count}",
                                                 chat_id=self.user_chat_id,
                                                 message_id=msg.id)
                ttt = self.events_controller.get_by(acc_id=i.acc_id,
                                                    name_type="Comment",
                                                    tg_id=self.group_id.replace("-100", ""),
                                                    tg_id_group=self.post_id,
                                                    )
                for y in ttt:
                    self.events_controller.delete(id=y.id)
                self.events_controller.create(acc_id=i.acc_id,
                                              name_type=f"Comment",
                                              tg_id=self.group_id.replace("-100", ""),
                                              tg_id_group=self.post_id)
                if count >= self.count:
                    break
                else:
                    await asyncio.sleep(random.uniform((self.COOLDOWN * (1.0 - (self.RANGE_COOLDOWN / 100))),
                                                       ((self.COOLDOWN * (1.0 + (self.RANGE_COOLDOWN / 100))))))
            except Exception as ex:
                error_count += 1
                print(ex)
            finally:
                await session_list.give_away_session(acc.phone)
        await self.bot.edit_message_text(text=f"[Статус Коментарі]\n"
                                               f"[{self.group_id}]\n"
                                              f"[Закінчено]\n"
                                               f"Готово: {count} з {self.count}\n"
                                               f"Помилок: {error_count}",
                                         chat_id=self.user_chat_id,
                                         message_id=msg.id)



