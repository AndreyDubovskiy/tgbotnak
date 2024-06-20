from telethon.errors import SessionPasswordNeededError
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError, UserDeletedError, UserInvalidError, UserDeactivatedError, UsernameInvalidError
from db.controllers.AccsController import AccsController

class AccSessionList:
    def __init__(self):
        self.ses_list = {} #{"name_session": {"session": obj; "count": int}}
        self.accs_controller = AccsController()

    async def start_session(self, name: str):
        tmp = self.accs_controller.get_by(name=name, is_active=True)
        if len(tmp) == 0:
            return False
        acc = tmp[0]
        if acc.proxy_id == None:
            self.ses_list[name] = {"session": TelegramClient(session=acc.session_name,
                                                             api_id=acc.api_id,
                                                             api_hash=acc.api_hash),
                                   "count": 0}
        else:
            self.ses_list[name] = {"session": TelegramClient(session=acc.session_name,
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
        await self.ses_list[name]["session"].connect()
        return True

    async def end_session(self, name:str):
        acc = self.ses_list.get(name, None)
        if acc == None:
            return False
        await acc["session"].disconnect()
        self.ses_list.pop(name)
        return True

    async def get_session(self, name:str):
        acc = self.ses_list.get(name, None)
        if acc == None:
            res = await self.start_session(name)
            if res:
                self.ses_list[name]["count"] += 1
                return self.ses_list[name]["session"]
            else:
                raise Exception("Session dont start")
        else:
            self.ses_list[name]["count"] += 1
            return self.ses_list[name]["session"]

    async def take_session(self, name:str):
        acc = self.ses_list.get(name, None)
        if acc == None:
            return False
        self.ses_list[name]["count"] -= 1
        if self.ses_list[name]["count"] <= 0:
            await self.end_session(name)
        return True