# ba_meta requite api 8
import bascenev1 as bs
import bascenev1._hooks
from admin.roles import whatRol
from logger.logs import LoggerControl
from .handle import sendmsg, is_server, get_uniqueid
from .cmds import handleCmd

prefixes = ["/", "!", ".", ",", "#", "?", "*", "@"]
prefix = tuple(prefix for prefix in prefixes)


def main(func):
    def deco(*args, **kwargs):
        msg = args[0]
        client_id = args[1]
        accountid = get_uniqueid(client_id)
        name = ""
        for ros in bs.get_game_roster():
            if ros["client_id"] == client_id:
                try:
                    name = ros["players"][0]["name_full"]
                except:
                    name = ros["display_string"]

        rol = whatRol(accountid)
        if client_id == -1:
            return msg
        if msg.startswith(prefix):
            handleCmd(msg, client_id)
            # LoggerControl(msg, accountid, rol, name).log()
            return None

        return func(*args, **kwargs)

    return deco
