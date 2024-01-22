# ba_meta require api 8
# by: zeenppay
import random
import bascenev1 as bs
import _babase
import babase


class effectAmbient(bs.Actor):
    """clase que crea efectos de ambiente para los mapas."""

    def __init__(self, bounds, random_text:bool=False):
        super().__init__()

        self.bounds = (
            random.uniform(bounds[0], bounds[3]),
            random.uniform(bounds[1], bounds[4]) - 1.0,
            random.uniform(bounds[2], bounds[5]),
        )

        # No collision
        self.no_collision = bs.Material()
        self.no_collision.add_actions(
            actions=(
                ("modify_part_collision", "collide", False),
                ("modify_part_collision", "physical", False),
            )
        )
        if random_text:
            tex_random = random.choice(["bonesColorMask", "aliColorMask", "egg2", "egg4", "egg1"])

        self.particle = bs.newnode(
            "prop",
            delegate=self,
            attrs={
                "position": self.bounds,
                "velocity": (0, 1, 0),
                "mesh": bs.getmesh("box"),
                "mesh_scale": 0.08,
                "color_texture": bs.gettexture("null" if not random_text else tex_random),
                "body": "crate",
                "gravity_scale": 1,
                "shadow_size": 0.1,
                "reflection": "soft",
                "reflection_scale": [5],
                "body_scale": 0.1,
                "extra_acceleration": (0, 20, 0), # floten verticalmente hacia arriba :p
                # "damping": 999 * 999,
                "materials": [self.no_collision],
            },
        )

        light = bs.newnode(
            "light",
            owner=self.particle,
            attrs={
                "height_attenuated": False,
                "color": (1.0, 0.8, 0.4),
            },
        )
        self.particle.connectattr("position", light, "position")

        bs.animate(
            light,
            "radius",
            {0: 0, 1: 0.06, 4: 0}
        )
        bs.animate(
            light,
            "intensity",
            {0: 0, 1: 0.7, 4: 0}
        )


        bs.animate(
            self.particle,
            "mesh_scale",
            {0.0: 0, 4: self.particle.mesh_scale, 8: 0.0},
            loop=True,
        )
        self._die_timer = bs.timer(
            4.0, bs.WeakCall(self.handlemessage, bs.DieMessage())
        )

    def dead_cube(self):
        if hasattr(self, "particle") or self.particle.exists():
            bs.timer(10.5, self.particle.delete)
            #print("Particle deleted.") # debug

    def handlemessage(self, m):
        if isinstance(m, bs.DieMessage):
            self.dead_cube()
        elif isinstance(m, bs.OutOfBoundsMessage):
            self.handlemessage(bs.DieMessage(how=bs.DeathType.OUT_OF_BOUNDS))


def create_particles(count: int):
    activity = bs.get_foreground_host_activity()
    if activity is not None:
        if not hasattr(activity, "cubes"):
            activity.cubes = []
        
        if hasattr(activity, "map"):
            bounds = activity.map.get_def_bound_box("area_of_interest_bounds")
            new_cubes = []
            for _ in range(count):
                with activity.context:
                    cube = effectAmbient(bounds)
                    new_cubes.append(cube)

            
            for cube in activity.cubes:
                cube.handlemessage(bs.DieMessage())
            activity.cubes = new_cubes




def gen_cubes(activity):
    create_particles(random.randint(1, 2))
    bs.timer(0.8, babase.Call(gen_cubes, activity), repeat=False)


bs._activity.Activity.cubegenerator = gen_cubes
