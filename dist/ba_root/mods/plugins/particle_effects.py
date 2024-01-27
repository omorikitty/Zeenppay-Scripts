# ba_meta require api 8
# by: zeenppay
import random
import bascenev1 as bs
import _babase
import babase
from bascenev1lib.gameutils import SharedObjects
from bascenev1lib.actor.spazfactory import SpazFactory
from bascenev1._messages import OutOfBoundsMessage, DieMessage, DeathType


class effectAmbient(bs.Actor):
    """clase que crea efectos de ambiente para los mapas."""

    def __init__(self, bounds, random_text: bool = False):
        bs.Actor.__init__(self)

        self.bounds = (
            random.uniform(bounds[0], bounds[3]),
            random.uniform(bounds[1], bounds[4]),
            random.uniform(bounds[2], bounds[5]),
        )

        # No collision
        self.no_collision = bs.Material()
        self.no_collision.add_actions(
            conditions=("they_have_material", SpazFactory.get().punch_material),
            actions=(
                ("modify_part_collision", "collide", False),
                ("modify_part_collision", "physical", False),
            ),
        )

        if random_text:
            tex_random = random.choice(
                ["bonesColorMask", "aliColorMask", "egg2", "egg4", "egg1"]
            )

        self.particle = bs.newnode(
            "prop",
            delegate=self,
            attrs={
                "position": self.bounds,
                "velocity": (0, 1, 0),
                "mesh": bs.getmesh("box"),
                "mesh_scale": 0.072,
                "color_texture": bs.gettexture(
                    "null" if not random_text else tex_random
                ),
                "body": "crate",
                "gravity_scale": 0.0,
                "shadow_size": 0.8,
                "reflection": "powerup",
                "reflection_scale": [0],
                "body_scale": 0,
                "materials": [self.no_collision],
            },
        )

        self._animate()

    def _animate(self) -> None:
        if not self.particle:
            return
        bs.animate(
            self.particle,
            "mesh_scale",
            {
                0: 0,
                2: self.particle.mesh_scale,
                4: 0,
                5: self.particle.mesh_scale,
                6: 0,
            },
            loop=True,
        )

    def handlemessage(self, msg):
        assert not self.expired
        if isinstance(msg, DieMessage):
            if self.particle:
                self.particle.delete()
                # print("Destroy")  # debug
        elif isinstance(msg, OutOfBoundsMessage):
            self.handlemessage(DieMessage(how=DeathType.OUT_OF_BOUNDS, immediate=True))
            # print("Particle Deleted.")  # debug
        else:
            super().handlemessage(msg)


def create_particles(count: int):
    activity = bs.get_foreground_host_activity()
    if activity is not None:
        if not hasattr(activity, "cubes"):
            activity.cubes = []

        if hasattr(activity, "map"):
            bounds = activity.map.get_def_bound_box("area_of_interest_bounds")
            for _ in range(count):
                with activity.context:
                    cube = effectAmbient(bounds).autoretain()
                    activity.cubes.append(cube)
                    # print(len(activity.cubes)) # debug

            for cube in activity.cubes:
                if cube.particle.exists():
                    bs.timer(
                        7.5,
                        babase.Call(cube.particle.handlemessage, DieMessage()),
                    )
            activity.cubes = []


def gen_cubes(activity):
    create_particles(1)
    bs.timer(0.4, babase.Call(gen_cubes, activity))


bs._activity.Activity.cubegenerator = gen_cubes
