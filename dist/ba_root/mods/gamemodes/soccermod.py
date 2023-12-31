from __future__ import annotations

from typing import TYPE_CHECKING
import random
import babase
import bascenev1 as bs
import bascenev1lib
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.game.hockey import PuckDiedMessage, Player, Team, HockeyGame
from bascenev1lib.gameutils import SharedObjects
from bascenev1lib.actor.scoreboard import Scoreboard, _Entry
from bascenev1lib.actor.powerupbox import PowerupBoxFactory

if TYPE_CHECKING:
    from typing import Any, Sequence, Dict, Type, List, Optional, Union

# Released under the MIT License. See LICENSE for details.
#
"""Implements football games (both co-op and teams varieties)."""


"""
Lista de cambios:

- Mejor Game Feel al Golpear el Balon
- Se Cambio el Scoreboard a Uno Mas Simple
- Se Añadio Un Localizador Para Preever Donde Caera La Bola

Nota: Esto Es Un Port del Mod de Futbol Soccer Creado 
Por oore282 Todo Los Creditos Para el Solo Añadi Pequeñas Modificaciones

Creditos: oore282
portBy: Zeenppay
"""

# ba_meta require api 8
# (see https://ballistica.net/wiki/meta-tag-system)





class board(Scoreboard):
    """Decoraremos el scoreboard para que se vea mas minimalista"""
    def __init__(self, label: bs.Lstr | None = None, score_split: float = 0.7):
        super().__init__()

        if not isinstance(bs.getsession(), bs.FreeForAllSession):
            self._do_cover = False
            self._spacing = 30.0
            self._pos = (20.0, -70.0)
            self._scale = 0.9
            self._flash_length = 1


bascenev1lib.actor.scoreboard.Scoreboard = board

class Puck(bs.Actor):
    """A lovely giant hockey puck."""

    def __init__(self, position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()

        # Spawn just above the provided point.
        self._spawn_pos = (position[0], position[1] + 1.0, position[2])
        self.last_players_to_touch: Dict[int, Player] = {}
        self.scored = False
        assert activity is not None
        assert isinstance(activity, SoccerGame)
        pmats = [shared.object_material, activity.puck_material]
        self.node = bs.newnode('prop',
                               delegate=self,
                               attrs={
                                   'mesh': bs.getmesh('shield'),
                                   'color_texture':
                                        bs.gettexture('discordLogo'),
                                   'body': 'sphere',
                                   'body_scale': 1,
                                   'reflection': 'soft',
                                   'reflection_scale': [0.1],
                                   'shadow_size': 0.5,
                                   'is_area_of_interest': True,
                                   'position': self._spawn_pos,
                                   'materials': pmats
                               })
        bs.animate(self.node, 'mesh_scale', {0: 0, 0.1: 0.2, 0.2: 0.3})
        self._localizeBall()

    def _localizeBall(self):
        """
        Simplemente nos ayudara ubicar la pelota cuando avienten
        la pelota por los aires, pensemos en los porteros que le hechan gol
        por un fallo de perspectiva
        """

        attr = [
            {
                'shape': 'circle',
                'color': (1, 1, 1),
                'opacity':0.05,
                'size': [1],
                'draw_beauty': True,
                'additive': False
            },

            {
                'shape': 'circleOutline',
                'size':[1],
                'opacity': 0.1,
                'color': (1, 1, 0),
                'draw_beauty': False,
                'additive': True
            }

        ]

        for i in attr:
            loc = bs.newnode('locator', 
                owner=self.node, 
                attrs=i)
            self.node.connectattr('position', loc,
                                  'position')
        

    def _puckAnim(self, msg):
        """ 
        Esa funcion añade animacion y efectos a la pelota
        para un mejor game feel en nuestro gameplay no queremos que nuestro
        balon sea aburrido todo el tiempo :p
            
        """
        from bascenev1lib.actor.popuptext import PopupText
        
        # comprueba que la pelota aun este viva xd :p
        if not self.node.exists():
            return

        assert msg.force_direction is not None

        # reproduce este sonido cuando pegen a la bola
        bs.getsound('pop01').play(0.4, position=self.node.position)

        
        # emitir particulas tambien le da un toque jeje
        for _ in range(10):
            bs.emitfx(position=msg.pos,
                      velocity=(msg.force_direction[0] * 2.0,
                                msg.force_direction[1] * 2.0,
                                msg.force_direction[2] * 2.0),
                      spread=1.0,
                      emit_type='fairydust')


        # Esto le dara una capa extra de ezquisites ulala..
        punchpos = (msg.pos[0] + msg.force_direction[0] * 0.02,
                    msg.pos[1] + msg.force_direction[1] * 0.02,
                    msg.pos[2] + msg.force_direction[2] * 0.02)
        flash_color = (1.0, 0.8, 0.4)
        light = bs.newnode(
            'light',
            attrs={
                'position': punchpos,
                'radius': 0.3,
                'intensity': 0.7 ,
                'height_attenuated': False,
                'color': flash_color
            })
        bs.timer(0.06, light.delete)

        flash = bs.newnode('flash',
                            attrs={
                                'position': punchpos,
                                'size': 0.5,
                                'color': (2,2,2)
                            })
        bs.timer(0.06, flash.delete)

        # crea una animacion rapida como de rebote
        # para que se vea que fue golpeada y no este
        # re dura como mi pito :p
        bs.animate(self.node, 'mesh_scale', {0: 0.3, 0.03: 0.5, 0.06: 0.3})
        

        # Cuando golpee la bola muestra un mensaje random
        PopupText(random.choice(
            ['Bang!', 'Egoist!', 'HAHA!', 'Maradona!', 'XD']),position=self.node.position, color=(2,2,2)).autoretain()

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            assert self.node
            self.node.delete()
            activity = self._activity()
            if activity and not msg.immediate:
                activity.handlemessage(PuckDiedMessage(self))



        # If we go out of bounds, move back to where we started.
        elif isinstance(msg, bs.OutOfBoundsMessage):
            assert self.node
            self.node.position = self._spawn_pos

        elif isinstance(msg, bs.HitMessage):
            assert self.node
            assert msg.force_direction is not None
            self.node.handlemessage(
                'impulse', msg.pos[0], msg.pos[1], msg.pos[2], msg.velocity[0],
                msg.velocity[1], msg.velocity[2], 1.0 * msg.magnitude,
                1.0 * msg.velocity_magnitude, msg.radius, 0,
                msg.force_direction[0], msg.force_direction[1],
                msg.force_direction[2])

            self._puckAnim(msg)

            # If this hit came from a player, log them as the last to touch us.
            s_player = msg.get_source_player(Player)
            if s_player is not None:
                activity = self._activity()
                if activity:
                    if s_player in activity.players:
                        self.last_players_to_touch[s_player.team.id] = s_player
        else:
            super().handlemessage(msg)


# ba_meta export bascenev1.GameActivity
class SoccerGame(HockeyGame):
    """Football game for teams mode."""

    name = 'Futbol Soccer'
    description = 'futbolito MOD: oore282'
    available_settings = [
        bs.IntSetting(
            'Score to Win',
            min_value=1,
            default=1,
            increment=1,
        ),
        bs.IntChoiceSetting(
            'Time Limit',
            choices=[
                ('None', 0),
                ('1 Minute', 60),
                ('2 Minutes', 120),
                ('5 Minutes', 300),
                ('10 Minutes', 600),
                ('20 Minutes', 1200),
            ],
            default=0,
        ),
        bs.FloatChoiceSetting(
            'Respawn Times',
            choices=[
                ('Shorter', 0.25),
                ('Short', 0.5),
                ('Normal', 1.0),
                ('Long', 2.0),
                ('Longer', 4.0),
            ],
            default=1.0,
        ),
        bs.BoolSetting('Boxing Gloves', default=False),
        bs.BoolSetting('Enable Powerups', default=True),
        bs.BoolSetting('Ice Floor', default=True),
        bs.BoolSetting('Epic Mode', default=False),
    ]

    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return issubclass(sessiontype, bs.DualTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[bs.Session]) -> List[str]:
        assert bs.app.classic is not None
        return bs.app.classic.getmaps('hockey')

    def __init__(self, settings: dict):
        super().__init__(settings)
        shared = SharedObjects.get()
        self._scoreboard = board()
        self._cheer_sound = bs.getsound('cheer')
        self._chant_sound = bs.getsound('crowdChant')
        self._foghorn_sound = bs.getsound('foghorn')
        self._swipsound = bs.getsound('swip')
        self._whistle_sound = bs.getsound('refWhistle')
        self.puck_model = bs.getmesh('puck')
        self.puck_tex = bs.gettexture('puckColor')
        self._puck_sound = bs.getsound('ballSound')
        self._boxing_gloves = bool(settings.get('Boxing Gloves', False))
        self._enable_powerups = bool(settings.get('Enable Powerups', True))
        self._ice_floor = bool(settings.get('Ice Floor', True))
        self._epic_mode = bool(settings['Epic Mode'])
        # Base class overrides:
        self.slow_motion = self._epic_mode
        self.default_music = (bs.MusicType.EPIC
                              if self._epic_mode else bs.MusicType.FOOTBALL)
        self.puck_material = bs.Material()
        self.puck_material.add_actions(actions=(('modify_part_collision',
                                                 'friction', 0.5)))
        self.puck_material.add_actions(conditions=('they_have_material',
                                                   shared.pickup_material),
                                       actions=('modify_part_collision',
                                                'collide', False))
        self.puck_material.add_actions(
            conditions=(
                ('we_are_younger_than', 100),
                'and',
                ('they_have_material', shared.object_material),
            ),
            actions=('modify_node_collision', 'collide', False),
        )
        self.puck_material.add_actions(conditions=('they_have_material',
                                                   shared.footing_material),
                                       actions=('impact_sound',
                                                self._puck_sound, 0.2, 5))

        # Keep track of which player last touched the puck
        self.puck_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(('call', 'at_connect', self._handle_puck_player_collide),),
        )

        # We want the puck to kill powerups; not get stopped by them
        self.puck_material.add_actions(
            conditions=('they_have_material',
                        PowerupBoxFactory.get().powerup_material),
            actions=(('modify_part_collision', 'physical', False),
                     ('message', 'their_node', 'at_connect', bs.DieMessage())))
        self._score_region_material = bs.Material()
        self._score_region_material.add_actions(
            conditions=('they_have_material', self.puck_material),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', False),
                ('call', 'at_connect', self._handle_score),
            ),
        )
        self._puck_spawn_pos: Sequence[float] | None = None
        self._score_regions: list[bs.NodeActor] | None = None
        self._puck: Puck | None = None
        self._score_to_win = int(settings['Score to Win'])
        self._time_limit = float(settings['Time Limit'])


    

    def on_transition_in(self) -> None:
        super().on_transition_in()
        shared = SharedObjects.get()
        activity = bs.getactivity()
        if self._ice_floor:
            activity.map.is_hockey = True
        else:
            activity.map.is_hockey = False
        activity.map.node.materials = [shared.footing_material]
        activity.map.floor.materials = [shared.footing_material]
        activity.map.floor.color = (0.1, 1.0, 0.1)

    def on_begin(self) -> None:
        
        self.setup_standard_time_limit(self._time_limit)
        if self._enable_powerups:
            self.setup_standard_powerup_drops()
        else:
            pass
        self._puck_spawn_pos = self.map.get_flag_position(None)
        self._spawn_puck()

        # Set up the two score regions.
        defs = self.map.defs
        self._score_regions = []
        self._score_regions.append(
            bs.NodeActor(
                bs.newnode(
                    'region',
                    attrs={
                        'position': defs.boxes['goal1'][0:3],
                        'scale': defs.boxes['goal1'][6:9],
                        'type': 'box',
                        'materials': [self._score_region_material],
                    },
                )
            )
        )
        self._score_regions.append(
            bs.NodeActor(
                bs.newnode(
                    'region',
                    attrs={
                        'position': defs.boxes['goal2'][0:3],
                        'scale': defs.boxes['goal2'][6:9],
                        'type': 'box',
                        'materials': [self._score_region_material],
                    },
                )
            )
        )
        self._update_scoreboard()
        self._chant_sound.play()

    
    def spawn_player(self, player: Player) -> bs.Actor:
        spaz = self.spawn_player_spaz(player)
        if self._boxing_gloves:
            spaz.equip_boxing_gloves()

        spaz.connect_controls_to_player (enable_punch=True,
                                                                     enable_jump=True,
                                                                     enable_bomb=True,
                                                                     enable_pickup=False)

    def _spawn_puck(self) -> None:
        self._swipsound.play()
        self._whistle_sound.play()
        self._flash_puck_spawn()
        assert self._puck_spawn_pos is not None
        self._puck = Puck(position=self._puck_spawn_pos)
