# -*- coding: utf-8 -*-
# ba_meta require api 8

import bascenev1 as bs
import babase
import _babase
from .handle import (
    sendmsg,
    playerFromClientID,
    is_admin,
    is_server,
    get_uniqueid,
    extract_command,
    myactor,
    all_player_actor,
    everyone,
)
from admin import roles
from .cmdManager import CommandManager
import time
import threading

publicCmd = ["uniqueid", "list", "love", "cmds"]
adminCommand = [
    "admin",
    "kick",
    "end",
    "restart",
    "head",
    "godspeed",
    "explodehead",
    "gravity",
]
manager = CommandManager()


def authorize(client_id: int, msg: str):
    """Comprueba si el accountid esta autorizado a usar comandos.

    Args:
        client_id (int): Cliente del jugador.
        msg (str): Mensaje que envio.

    Returns:
        bool: True si es un admin, False en caso contrario.
    """
    uniqueid = get_uniqueid(client_id)
    cmd = extract_command(msg)
    # print(is_server(uniqueid))
    # print(is_admin(uniqueid))
    if is_admin(uniqueid) or is_server(uniqueid):
        return True
    elif cmd in publicCmd:
        return True
    else:
        return False  # No admin


def admin_command(func):
    """Verifica si el jugador tiene un rol."""

    def wrapper(msg, client_id):
        if authorize(client_id, msg):
            func(msg, client_id)
        else:
            sendmsg("Tu ere pobre, tu no tiene admin.", client_id)

    return wrapper


@admin_command
def handleCmd(
    msg: str,
    client_id: int,
    public_cmds: list[str] = publicCmd,
    admin_cmds: list[str] = adminCommand,
):
    """Permite manipular los comandos y ajustar la funcion que ejerce cada uno.

    Args:
        msg (str): Mensaje que envio.
        client_id (int): Cliente del jugador.
        public_cmds (list): Comandos publicos. Defaults to publicCmd.
        admin_cmds (list): Comandos de administrador. Defaults to adminCommand.
    """
    command = extract_command(msg)
    argument = msg.split(" ")[1:]
    uniqueID = get_uniqueid(client_id)

    if not command in public_cmds + admin_cmds:
        sendmsg(f"El comando {command} no existe.", client_id)
        return

    if not manager.process_command(command, client_id, uniqueID):
        return
    try:
        if command in ["uniqueid", "id", "pb"]:
            account_id(argument, client_id, uniqueID)

        elif command in ["list", "ls"]:
            list_player(client_id)

        elif command in ["love", "hug"]:
            love(argument, client_id)

        elif command == "cmds":
            cmds = [i for i in public_cmds]
            sendmsg(cmds, client_id)

        elif command == "kick":
            kick(argument, client_id)

        elif command == "end":
            end(argument)

        elif command == "restart":
            restart(argument)

        elif command == "godspeed":
            goSpeed(argument, client_id)

        elif command == "head":
            head(argument, client_id)

        elif command == "explodehead":
            explodeHead(argument)

        elif command == "gravity":
            gravity(argument)

    except Exception as e:
        sendmsg(f"Error: {e}", client_id)
        print(e)
        return


def end(argument):
    """Finaliza la partida al siguiente juego o mapa"""
    if not argument or argument == [""]:
        with bs.get_foreground_host_activity().context:
            bs.get_foreground_host_activity().end_game()
            bs.broadcastmessage("Finalizando Partida...")


def restart(argument):
    """Reinicia el servidor"""
    if not argument or argument == [""]:
        babase.quit(confirm=False, quit_type=babase.QuitType.HARD)
    else:
        return


def goSpeed(argument, clientid):
    """Velocidad de dios i love you killua <3"""
    if not argument or argument[""]:
        player = myactor(clientid)
        player.node.hockey = True

    elif argument[0] == "all":
        a = all_player_actor()
        a.node.hockey = True
    else:
        player = myactor(int(argument[0]))
        player.node.hockey = True

    sendmsg("Killua God Speed", clientid, color=(0.5, 0.4, 0.8))


def gravity(argument):
    moon = None
    if not argument or argument == [""]:
        with bs.get_foreground_host_activity().context:
            player = all_player_actor()
            moon = bs.timer(1, babase.Call(gravityMoon, player.node), repeat=True)
    elif argument[0] == "off":
        if moon is not None:
            moon = None


def gravityMoon(node):
    if not node.exists():
        return
    node.handlemessage(
        "impulse",
        node.position[0],
        node.position[1],
        node.position[2],
        0,
        25,
        0,
        32,
        0.05,
        0,
        0,
        0,
        0.8,
        0,
    )


def explodeHead(argument):
    if not argument or argument == [""]:
        with bs.get_foreground_host_activity().context:
            for spaz in everyone():
                if spaz.node.head_mesh != None:
                    spaz.node.head_mesh = None
                    spaz.node.style = "bones"
                    spaz.node.handlemessage("knockout", 1000)
                    blast_head(spaz)


def blast_head(spaz):
    """Creates a fake decorative explosion."""
    pos = [p + (0.5 if i == 1 else 0) for i, p in enumerate(spaz.node.position)]
    vel = [v * 0.77 for v in spaz.node.velocity]

    explosion = bs.newnode(
        "explosion",
        attrs={
            "position": pos,
            "velocity": vel,
            "radius": 1.2,
            "color": spaz.node.color,
        },
    )

    bs.emitfx(
        position=pos,
        emit_type="distortion",
        spread=1.0,
    )
    bs.emitfx(position=pos, velocity=vel, count=6, spread=0.7, chunk_type="metal")

    bs.timer(2, explosion.delete)


def head(argument, clientid):
    if not argument or argument == [""]:
        player = myactor(clientid)
        player.node.hold_node = player.node
    elif argument[0] == "all":
        a = all_player_actor()
        a.node.hold_node = a.node
    else:
        choose_actor = myactor(int(argument[0]))
        choose_actor.node.hold_node = choose_actor.node


def kick(arguments, cid):
    """Expulsa al jugador del servidor."""
    if not arguments or arguments == [""]:
        sendmsg("Formato: /kick <client_id>", cid)
    else:
        cl_id = int(arguments[0])
        acid = get_uniqueid(cl_id)
        if not is_admin(acid) and not is_server(acid):
            bs.disconnect_client(cl_id)
        else:
            sendmsg("No se puede expulsar al host o a un administrador.", cid)
            return


def account_id(argument, clientid, accountid=None):
    """Retorna el Unique ID del jugador."""
    if not argument or argument == [""]:
        sendmsg(f"Tu uniqueid de cuenta es {accountid}.", clientid)
    else:
        try:
            arg = argument[0]
            player = playerFromClientID(int(arg))
            name = player.getname(icon=True)
            account_id = player.get_v1_account_id()
            sendmsg(f"El uniqueid de {name} es '{account_id}'.", clientid)
        except bs.PlayerNotFoundError:
            sendmsg(
                "Formato: /uniqueid <client_id> o <player_id>",
                clientid,
                color=(0.5, 0.8, 0.5),
            )
            return


def love(argument, clientid):
    """Envia un abrazo a tu mejor amigo."""
    if not argument or argument == [""]:
        sendmsg("Jugador no encontrado.", clientid)
    else:
        try:
            fro = playerFromClientID(clientid)
            fro_name = fro.getname(True, True)
            to = playerFromClientID(int(argument[0]))
            to_name = to.getname(True, True)
            to_client = to.inputdevice.client_id
            sendmsg(f"Acabas de enviar un abrazo a {to_name}.", clientid)
            sendmsg(f"{fro_name} te envia un fuerte abrazo <3!", to_client)

        except bs.PlayerNotFoundError:
            sendmsg(
                "Formato: /love <client_id> o <player_id>",
                clientid,
                color=(0.5, 0.8, 0.5),
            )
            return


def list_player(clientid):
    """Retorna una lista de los jugadores en la partida filtrando su ClientID y PlayerID."""
    p = "{0:^16}{1:^15}{2:^10}"
    separator = "\n______________________________\n"

    list_players = p.format("Nombre", "Client ID", "Player ID") + separator
    session = bs.get_foreground_host_session()

    for index, player in enumerate(session.sessionplayers):
        list_players += (
            p.format(player.getname(icon=False), player.inputdevice.client_id, index)
            + "\n"
        )

    sendmsg(list_players, clientid)