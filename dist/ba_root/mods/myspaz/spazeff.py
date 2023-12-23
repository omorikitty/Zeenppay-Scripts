import babase
import _babase
import bascenev1 as bs
import random
import weakref
from myspaz.tag import PermissionEffect

class decorator(object):

    """ 
    clase que nos ayudara a aplicar efecto a nuestro spaz
    parametros:
        node: para la referencia del nodo spaz
        player: argumento q nos servira para extraer el account_id                         
    """

    def __init__(self, node, player):
        self.node = node
        self.player=player
        if not isinstance(node, bs.Node) or not isinstance(player, bs.Player):
            return

        # Obtener el ID de la cuenta del jugador
        account_id = player._sessionplayer.get_v1_account_id()

        # Test
        if account_id is None or account_id != "pb-IF4xVUg4FA==":
            # no hagas nada si es que el account_id te retorna None
            return

        # Test Effects
        PermissionEffect(owner=self.node, tag="OWNER")
        self.timeEff = bs.Timer(0.2, bs.Call(self._set_fairydust), repeat=True)

    def _set_fairydust(self):
        if not self.node.exists() or not self.player.is_alive():
            self.timeEff = None
            return

        position = (self.node.torso_position[0], self.node.torso_position[1], self.node.torso_position[2])
        velocity = self.node.velocity
        bs.emitfx(
            position=position,
            velocity=velocity,
            count=20,
            spread=1.0,
            emit_type="fairydust",
        )

