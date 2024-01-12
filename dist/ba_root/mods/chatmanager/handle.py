# ba_meta require api 8
import bascenev1 as bs
from admin.roles import get_all_roles


prefixes = ["/", "!", ".", ",", "#", "?", "*", "@"]


def sendmsg(msg: str, client: int, color=None):
    """Envia un mensaje privado al jugador"""
    for m in msg.split("\n"):
        bs.chatmessage(m, clients=[client])
    bs.broadcastmessage(
        msg,
        clients=[client],
        transient=True,
        color=(1, 1, 1) if color is None else color,
    )


def extract_command(msg):
    """Esta funcion obtiene los comandos y añade nuevos prefijos"""
    for prefix in prefixes:
        if msg.startswith(prefix):
            # Elimina el prefijo y obten el comando
            return msg[len(prefix) :].split(" ")[0].lower()

    return


def get_uniqueid(client: int):
    """Retorna la uniqueid del jugador usando su client_id"""
    roster = bs.get_game_roster()
    for ros in roster:
        if ros is not None and ros != {} and ros["client_id"] == client:
            return ros["account_id"]

    return


def playerFromClientID(clientid: int):
    """Retorna el jugador indexado."""
    session = bs.get_foreground_host_session()
    # for client_id
    if len(str(clientid)) == 3:
        for i, player in enumerate(session.sessionplayers):
            if player.inputdevice.client_id == clientid:
                return player
    else:
        # for player_id
        if clientid < len(session.sessionplayers):
            return session.sessionplayers[clientid]

    return


def myactor(clientid: int):
    """Retorna el actor del jugador indexado.

    Args:
        clientid (int): clientID del jugador.

    Returns:
        player: jugador indexado
    """
    activity = bs.get_foreground_host_activity()
    # for client_id
    if len(str(clientid)) == 3:
        for i, player in enumerate(activity.players):
            if player.sessionplayer.inputdevice.client_id == clientid:
                return player.actor
    else:
        # for player_id
        if clientid < len(activity.players):
            return activity.players[clientid].actor

    return


def everyone():
    """Retorna Una Lista de Todos Los Jugadores en la Actividad.

    Returns:
        list: lista de jugadores en la actividad
    """
    allplayer: list = []
    activity = bs.get_foreground_host_activity().players
    for player in activity:
        if hasattr(player, "actor"):
            allplayer.append(player.actor)
    return allplayer


def all_player_actor():
    """Retorna el actor de todos los jugadores."""
    for i in bs.get_foreground_host_activity().players:
        if i is not None and i.exists() and i.is_alive():
            return i.actor


def is_server(pb):
    """Comprueba el servidor"""
    for i in bs.get_game_roster():
        if i["account_id"] == pb and i["client_id"] == -1:
            return True
    return False


def is_admin(pb):
    """Comprueba si el account_id esta en la lista de ids de los roles"""
    role = get_all_roles()
    for rol in role:
        if pb in role[rol]["id"]:
            return True
    return False
