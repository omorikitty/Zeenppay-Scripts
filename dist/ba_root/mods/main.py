# ba_meta require api 8

import sys
import os
import importlib
import _babase
import babase
from myspaz import spazmod

# ba_meta export babase.Plugin

class setup(babase.Plugin):
    def on_app_running(self):
        #print('HELLO!')
        runMods()


    def on_app_shutdown(self):
        print('Goodbye!')




def runMods():
    """
    esta funcion almacena todas nuestras modificaciones 
    """
    import_gamemodes()
    spazmod.run()

def import_gamemodes():
    """ Usaremos esta funcion para importar los modos de juegos de manera dinamica """
    sys.path.append(_babase.env()['python_directory_user'] + os.sep + "gamemodes")
    gamemodes = os.listdir("ba_root/mods/gamemodes")
    for gamemode in gamemodes:
        if gamemode.endswith(".py"):
            gamemode_name = gamemode.replace(".py", "")
            module_name = "gamemodes." + gamemode_name
            #print(f"Intentando importar: {module_name}")
            try:
                # importamos los modulos
                #print('Modos de jugo Importados Exitosamente!')
                __import__(module_name)
            except ImportError as e:
                print(f"Fallo al importar {module_name}: {e}")

    #print('Hello gamemodes!')


