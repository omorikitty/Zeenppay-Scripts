# ba_meta require api 8
import bascenev1 as bs
import babase
import json
import os
from chatmanager import handle


ROLES_PATH = os.path.join(babase.env().get("python_directory_user", ""), "admin.json")


def make_a_dir(name):
    """Crea un directorio en caso de que no exista"""
    if not os.path.exists(name):
        os.mkdir(name)


def dontAdmin(account):
    """Esta funcion basicamente comprueba si el account_id
    no se encuentra dentro de los roles

    retorna True si es que no se encuentra dentro
    de la listas de id que pertenecen a cada rol
    """
    rol = get_all_roles()
    if rol is not None:
        for i in rol.values():
            if account in i["id"]:
                return False
    return True


def add_account_rol(account: str, rol: str, name: str, clientid: int):
    """Otorga permisos de admin.

    Args:
        account (str): accountid.
        rol (str): rol ex: (owner,vip,admin,etc..)
        name (str): player name.
    """
    m = ""
    roles = get_all_roles()

    if rol in roles:
        role_id = roles[rol]["id"]

        if not account in role_id:
            try:
                role_id.append(account)
                m = f"{name} ha sido agregado exitosamente."
                save(roles)
            except Exception as e:
                m = f"Hubo un error al agregar el accountid: {e}"
                return
        else:
            m = f"{name} ya tiene un rol en {rol}."
            return
    else:
        m = f"{rol} no existe."
        return

    handle.sendmsg(m, clientid)


def remove_account_rol(account: str, rol: str, name: str, clientid: int):
    """Remueve el accountid del rol.

    Args:
        account (str): accountid.
        rol (str): rol ex: (owner,vip,admin,etc..)
        name (str): player name.
    """
    m = ""
    role = get_all_roles()
    role_id = role[rol]["id"]
    if rol in role and account in role_id:
        try:
            role_id.remove(account)
            m = f"{name} Ha sido Removido Existosamente.\n from rol: {rol}"
            save(role)
        except:
            m = "Hubo un error al agregar el accountid"
            return
    else:
        m = f"{rol} no existe"
        return

    handle.sendmsg(m, clientid)


def whatRol(account):
    """retorna el tipo de rol espesifico"""
    rol = get_all_roles()
    if rol is not None:
        for i, k in rol.items():
            if account in k["id"]:
                return i
    return


def get_all_roles():
    """Esta funcion nos retorna todos los roles que existen"""
    try:
        with open(ROLES_PATH, mode="r", encoding="utf-8") as rol:
            return json.load(rol)
    except FileNotFoundError:
        return None


def save(data: dict):
    """Guarda los cambios que hagamos en el admin.json"""
    with open(ROLES_PATH, mode="w", encoding="utf-8") as rol:
        json.dump(data, rol, indent=4)
