# ba_meta require api 8

import sys
import os
import bascenev1 as bs
import importlib
import _babase
import babase
import logging
import bascenev1._hooks
from plugins import importcustomcharacters, character_chooser, color_explosion, colorfulmaps2
from myspaz import spazmod



# ba_meta export babase.Plugin


class setup(babase.Plugin):
    def on_app_running(self):
        # print('HELLO!')
        runMods()

    def on_app_shutdown(self):
        print("Goodbye!")


def runMods():
    """
    esta funcion almacena todas nuestras modificaciones
    """
    logging.warning("Cargando mods...")
    import_gamemodes()
    spazmod.run()
    importcustomcharacters.enable()
    character_chooser.enable()
    color_explosion.enable()

def import_gamemodes():
    """Usaremos esta funcion para importar los modos de juegos de manera dinamica"""
    sys.path.append(_babase.env()["python_directory_user"] + os.sep + "gamemodes")
    success = False
    gamemodes = os.listdir("ba_root/mods/gamemodes")
    for gamemode in gamemodes:
        if gamemode.endswith(".py"):
            gamemode_name = gamemode.replace(".py", "")
            module_name = "gamemodes." + gamemode_name
            try:
                # importamos los modulos
                # print('Modos de jugo Importados Exitosamente!')
                success = True
                __import__(module_name)
            except ImportError as e:
                logging.warning(f"Fallo al importar {module_name}: {e}")

    if success:
        logging.warning("Minijuegos Importados Correctamente.")
    # print('Hello gamemodes!')
