import bascenev1 as bs
import babase
import json
import os


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
