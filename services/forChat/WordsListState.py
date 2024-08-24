import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
from db.controllers.GroupwordssController import GroupwordssController
from db.controllers.WordsController import WordsController
from db.models.GroupwordsModel import GroupwordsModel
import config_controller

class WordsListState(UserState):
    async def start_msg(self):
        self.groups_controller = GroupwordssController()
        self.words_controller = WordsController()

        self.MAX_ON_PAGE = 10

        self.groups = self.groups_controller.get_all()

        self.page_bool = False
        if len(self.groups) > self.MAX_ON_PAGE:
            self.page_bool = True

        self.current_page = 0

        self.edit = None
        self.current_group: GroupwordsModel = None

        return Response(
            text=f"Всього груп коментарів: {len(self.groups)}",
            buttons=markups.generate_list_groupswords(self.groups_controller.get_by(offset=self.current_page*self.MAX_ON_PAGE, limit=self.MAX_ON_PAGE), page=self.page_bool)
        )

    async def next_msg(self, message: str):
        if self.edit == "add":
            print("ADD")
            name_group = message
            self.groups_controller.create(name=name_group)
            return Response(text="Група створена!", redirect="/groups")
        elif self.edit == "addc":
            self.words_controller.create(name=message,
                                         group=self.current_group)
            return Response(text="Вводьте далі:",
                            buttons=markups.generate_cancel())

    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            if self.current_group != None:
                return Response(redirect="/groups")
            return Response(redirect="/menu")
        elif data_btn == "/next":
            self.current_page += 1
            tmp = self.groups_controller(offset=self.current_page*self.MAX_ON_PAGE, limit=self.MAX_ON_PAGE)
            if len(tmp) == 0:
                self.current_page -= 1
                tmp = self.groups_controller(offset=self.current_page*self.MAX_ON_PAGE, limit=self.MAX_ON_PAGE)
            return Response(
                        text=f"Всього груп коментарів: {len(self.groups)}",
                        buttons=markups.generate_list_groupswords(tmp, page=self.page_bool)
            )
        elif data_btn == "/back":
            if self.current_page > 0:
                self.current_page -= 1
            tmp = self.groups_controller(offset=self.current_page * self.MAX_ON_PAGE, limit=self.MAX_ON_PAGE)
            return Response(
                text=f"Всього груп коментарів: {len(self.groups)}",
                buttons=markups.generate_list_groupswords(tmp, page=self.page_bool)
            )
        elif data_btn == "/add":
            print("CLK BTN ADD")
            self.edit = "add"
            #return Response("Починайте вводити коментарі. Один коментар - одне повідомлення (тільки текст). \nЯк закінчите вводити натисніть 'Відміна'")
            return Response("Введіть назву групи коментарів:", buttons=markups.generate_cancel())
        elif data_btn == "/delete":
            self.groups_controller.delete(id=self.current_group.id)
            return Response(text="Видалено!",
                            redirect="/groups")
        elif data_btn == "/addc":
            self.edit = "addc"
            return Response(
                text="Починайте вводити коментарі. Один коментар - одне повідомлення (тільки текст). \nЯк закінчите вводити натисніть 'Відміна'",
                buttons=markups.generate_cancel()
            )
        else:
            try:
                id_group = int(data_btn)
                self.current_group = self.groups_controller.get_by(id=id_group)[0]
                return Response(text=f"Група коментарів: {self.current_group.name} \n"
                                     f"Кількість коментарів: {len(self.current_group.words)}",
                                buttons=markups.generate_groupswords())
            except Exception as ex:
                print("Error", ex)
                return Response(redirect="/groups")
