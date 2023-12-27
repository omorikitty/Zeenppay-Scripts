import babase
import bascenev1 as bs
import bascenev1lib
from bascenev1lib.actor.playerspaz import PlayerSpaz
from myspaz import tag, spazeff, turbo_punch
from typing import Sequence

class SpazPlayer(PlayerSpaz):
    """
    esta clase decora la clase PlayerSpaz la usaremos para aplicar nuestras modificaciones
    sin alterar la orginal
    """
    def __init__(self,
                 player: bs.Player,
                 color: Sequence[float] = (1.0, 1.0, 1.0),
                 highlight: Sequence[float] = (0.5, 0.5, 0.5),
                 character: str = 'Spaz',
                 powerups_expire: bool = True,):
        
        super().__init__(player=player,
                         color=color,
                         highlight=highlight,
                         character=character,
                         powerups_expire=powerups_expire,)


        try:
            spazeff.Decorator(self)
        except Exception as e:
            print(e)
            return 



def run():
    if turbo_punch.turboSpamming: turbo_punch.enable()
    bascenev1lib.actor.playerspaz.PlayerSpaz = SpazPlayer