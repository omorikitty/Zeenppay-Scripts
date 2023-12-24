import bascenev1 as bs
import babase
import json
import os

ROLES_PATH = os.path.join(babase.env().get("python_directory_user", ""), "admin/admin.json")

all_roles = [
    "owner", 
    "admin", 
    "vip"
]

def make_a_dir(name):
    """Crea un directorio en caso de que no exista"""
    if not os.path.exists(name):
        os.mkdir(name)

def dontAdmin(account):
    """Esta funcion basicamente comprueba si el account_id
       no se encuentra dentro de los roles

       retornara True si es que no se encuentra dentro
       de la lista 
    """
    rol = get_all_roles()
    if rol is not None:
        for i in all_roles:
            if account not in rol[i]["id"]:
                return True
                break

def whatRol(account):
    """retorna el tipo de rol espesifico 
    """
    if id is None:
        return

    for i in all_roles:
        if account in get_all_roles()[i]["id"]:
            return i
            break  


def get_all_roles():
    """Esta funcion nos retorna todos los roles que existen
    """
    try:
        with open(ROLES_PATH, mode="r",  encoding="utf-8") as rol:
            return json.load(rol)
    except:
        return None

def save(data: dict):
    """Guarda los cambios que hagamos en el admin.json"""
    with open(ROLES_PATH, mode="w", encoding="utf-8") as rol:
        json.dump(data, rol, indent=4)