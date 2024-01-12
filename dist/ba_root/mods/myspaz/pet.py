# bs_meta require api 8
"""mod created by PatronModz port to api 8"""
from __future__ import annotations
from typing import TYPE_CHECKING

import bascenev1 as bs
import random
import os
from bascenev1lib.actor import powerupbox as pb
from bascenev1lib.actor import playerspaz as ps


class LittlePet(bs.Actor):
    def __init__(
        self,
        node: bs.Node = None,
        item: str = "item1",
        position: Sequence[float] = (0.0, 1.0, 0.0),
    ):
        super().__init__()
        self.owner = node
        self.multitex = []
        self.no_collision = bs.Material()
        self.no_collision.add_actions(
            actions=(("modify_part_collision", "collide", False))
        )

        pfac = pb.PowerupBoxFactory.get()
        model, tex = self._get_model_and_texture(item)
        mats = [self.no_collision, pfac.powerup_material]
        scale = self._get_scale(item)
        body = self._get_body(item)
        type = self._get_type(item)
        ref, refs = self._get_reflection_values(item)
        if isinstance(tex, list):
            self.multitex = [t for t in tex]
            tex = tex[0]

        position = (position[0], position[1] + 5, position[2])
        self.node = bs.newnode(
            type,
            owner=self.owner,
            delegate=self,
            attrs={
                "body": body,
                "position": position,
                "mesh": model,
                "color_texture": tex,
                "reflection": ref,
                "mesh_scale": scale,
                "shadow_size": 0.2,
                "reflection_scale": [refs],
                "materials": mats,
            },
        )
        self._move()

        if type == "bomb":
            self.node.fuse_length = 0.5

        if any(self.multitex):
            self.changing_textures()

    def _get_model_and_texture(self, item):
        return {
            "item1": (bs.getmesh("aliHead"), bs.gettexture("aliColor")),
            "item2": (
                bs.getmesh("impactBomb"),
                [bs.gettexture("impactBombColor"), bs.gettexture("impactBombColorLit")],
            ),
            "item3": (bs.getmesh("frostyHead"), bs.gettexture("frostyColor")),
            "item4": (
                bs.getmesh("shield"),
                [bs.gettexture("powerupIceBombs"), bs.gettexture("aliColorMask")],
            ),
            "item5": (bs.getmesh("puck"), bs.gettexture("puckColor")),
            "item6": (bs.getmesh("egg"), bs.gettexture("eggTex1")),
            "item7": (bs.getmesh("powerup"), bs.gettexture("discordLogo")),
            "item8": (
                bs.getmesh("landMine"),
                [bs.gettexture("landMine"), bs.gettexture("landMineLit")],
            ),
            "item9": (bs.getmesh("bombSticky"), bs.gettexture("bombStickyColor")),
            "item10": (
                bs.getmesh("shrapnelSlime"),
                [bs.gettexture("cyborgColor"), bs.gettexture("bunnyColor")],
            ),
        }.get(item, (bs.getmesh("aliHead"), bs.gettexture("aliColor")))

    def _get_scale(self, item):
        return {
            "item4": 0.15,
            "item5": 0.5,
            "item6": 0.4,
            "item2": 0.7,
            "item7": 0.6,
            "item10": 0.2,
        }.get(item, 0.8)

    def _get_body(self, item):
        return {
            "item5": "puck",
            "item6": "puck",
        }.get(item, "box")

    def _get_type(self, item):
        return {
            "item9": "bomb",
        }.get(item, "prop")

    def _get_reflection_values(self, item):
        return {
            "item2": ("powerup", 1.0),
            "item4": ("powerup", 1.0),
            "item8": ("powerup", 1.0),
            "item9": ("sharper", 1.8),
        }.get(item, ("soft", 0.2))

    def changing_textures(self):
        self.texture_sequence = bs.newnode(
            "texture_sequence",
            owner=self.node,
            attrs={"rate": 100, "input_textures": self.multitex},
        )
        self.texture_sequence.connectattr("output_texture", self.node, "color_texture")

    def _move(self):
        t = 0.1
        self.pos_timer = bs.Timer(t, bs.WeakCall(self.update_pos, t), repeat=True)

    def update_pos(self, t: float):
        if not self.node.exists():
            if self.pos_timer is not None:
                self.pos_timer = None
            return

        calls = []

        def vel(t):
            t = max(t, 0)
            n = list(self.node.velocity)
            p = list(self.owner.velocity)
            bs.animate_array(self.node, "velocity", 3, {0: n, t: p})
            bs.timer(
                0.3,
                lambda: calls[1](
                    t,
                    [
                        random.random() * 1.5,
                        random.choice([0.8, 0.9, 1.0, 0.5]),
                        random.choice([0.3]),
                    ],
                ),
            )

        calls.append(vel)

        def pos(t, l):
            if not self.node.exists():
                return
            n = list(self.node.position)
            p = list(self.owner.position)
            p[1] += l[0]
            p[0] = p[0] + l[1] if p[0] < 0 else p[0] - l[1]
            t = max(t + l[2], 0)
            bs.animate_array(self.node, "position", 3, {0: n, t: p})

        calls.append(pos)
        bs.timer(0.0, lambda: calls[0](t * 2))

    def die(self):
        if hasattr(self, "node") or self.node.exists():
            self.node.delete()

    def handlemessage(self, m):
        if isinstance(m, bs.DieMessage):
            self.die()
        elif isinstance(m, bs.OutOfBoundsMessage):
            self.handlemessage(bs.DieMessage(bs.DeathType.OUT_OF_BOUNDS))
        else:
            super().handlemessage(m)


def add_pet(obj: str, node=None, position=None):
    LittlePet(item=obj, node=node, position=position).autoretain()
