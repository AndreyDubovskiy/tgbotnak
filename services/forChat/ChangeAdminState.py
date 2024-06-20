import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller

class ChangeAdminState(UserState):
    async def start_msg(self):
        return Response(text="Введіть наступним повідомленням новий пароль: ", buttons=markups.generate_cancel())

    async def next_msg(self, message: str):
        if config_controller.change_password_admin(self.user_chat_id, message):
            return Response(text="Пароль змінено!", redirect="/menu")
        else:
            return Response(text="Щось пішло не так! Можливо ви не увійшли під паролем", redirect="/menu")

    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            return Response(redirect="/menu")