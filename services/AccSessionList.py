from telethon.errors import SessionPasswordNeededError
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError, UserDeletedError, UserInvalidError, UserDeactivatedError, UsernameInvalidError
from db.controllers.AccsController import AccsController

class AccSessionList:
    def __init__(self):
        self.ses_list = {} #{"name_session": {"session": obj; "count": int}}
        self.accs_controller = AccsController()

        self.path_sessions = "saved/sessions/"

    async def start_session(self, phone: str):

        print("Start session", phone)
        tmp = self.accs_controller.get_by(phone=phone, is_active=True)
        if len(tmp) == 0:
            return False
        acc = tmp[0]
        if acc.proxy_id == None:
            self.ses_list[phone] = {"session": TelegramClient(session=self.path_sessions+acc.session_name,
                                                             api_id=acc.api_id,
                                                             api_hash=acc.api_hash),
                                   "count": 0}
        else:
            self.ses_list[phone] = {"session": TelegramClient(session=self.path_sessions+acc.session_name,
                                                             api_id=acc.api_id,
                                                             api_hash=acc.api_hash,
                                                             proxy=(
                                                                 acc.proxy.type_proxy,
                                                                 acc.proxy.ip,
                                                                 acc.proxy.port,
                                                                 True,
                                                                 acc.proxy.login,
                                                                 acc.proxy.password
                                                             )),
                                   "count": 0}
        await self.ses_list[phone]["session"].connect()
        return True

    async def end_session(self, phone:str):
        acc = self.ses_list.get(phone, None)
        if acc == None:
            return False
        await acc["session"].disconnect()
        self.ses_list.pop(phone)
        return True

    async def get_session(self, phone:str):
        acc = self.ses_list.get(phone, None)
        if acc == None:
            res = await self.start_session(phone)
            if res:
                self.ses_list[phone]["count"] += 1
                return self.ses_list[phone]["session"]
            else:
                raise Exception("Session dont start")
        else:
            self.ses_list[phone]["count"] += 1
            return self.ses_list[phone]["session"]

    async def give_away_session(self, phone:str):
        acc = self.ses_list.get(phone, None)
        if acc == None:
            return False
        self.ses_list[phone]["count"] -= 1
        if self.ses_list[phone]["count"] <= 0:
            await self.end_session(phone)
        return True


session_list = AccSessionList()