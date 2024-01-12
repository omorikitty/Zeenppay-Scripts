import babase
import _babase
import bascenev1 as bs
import random
import weakref
from myspaz.tag import PermissionEffect
from admin import roles
from .pet import add_pet

rol = roles.get_all_roles()
class Decorator(object):

    """ 
    clase que nos ayudara a aplicar efecto a nuestro spaz                        
    """

    def __init__(self, spaz):
        self.spaz = spaz
        # Obtener el ID de la cuenta del jugador
        account_id = spaz._player._sessionplayer.get_v1_account_id()
        

        # No hagas nada si el account id no está en la lista de roles
        # Tambien si no se consigue el account id del jugador
        if account_id is None or roles.dontAdmin(account_id):
            return

        self.timeEff = bs.Timer(0.2, bs.Call(self._set_fairydust), repeat=True)

        # Aplica el tag especifico de cada rol
        myrol = roles.whatRol(account_id)
        PermissionEffect(owner=spaz.node, tag=rol[myrol]["tag"], color=rol[myrol]["color"])
        add_pet(obj="item7", node=spaz.node, position=spaz.node.position)

    def _set_fairydust(self):
        if self.spaz is None or not self.spaz.node.exists() or not self.spaz.is_alive():
            self.timeEff = None
            return

        position = self.spaz.node.torso_position
        velocity = self.spaz.node.velocity
        bs.emitfx(
            position=position,
            velocity=velocity,
            emit_type="fairydust",
        )

