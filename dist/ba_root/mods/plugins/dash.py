# ba_meta require api 8
# mod by fryqss


import bascenev1 as bs
from bascenev1lib.actor.spaz import Spaz


def new_hook(spaz: Spaz) -> None:
    spaz.old_hook()
    time = (int(bs.time() * 1000.0) - spaz.last_punch_time_ms)
    #print(time) # debug
    node = spaz.node

    if spaz.dash_enabled is False \
    or node.exists() is False \
    or node.knockout > 0.0 \
    or node.frozen > 0.0 \
    or spaz.last_punch_time_ms == -9999 \
    or time < 1000:
        return

    def impulse() -> None:
        node.handlemessage(
            'impulse',
            node.position[0],
            node.position[1],
            node.position[2],
            node.move_left_right * 30,
            node.position[1] + 5,
            node.move_up_down * -30,
            5,
            5,
            0,
            0,
            node.move_left_right * 30,
            node.position[1] + 5,
            node.move_up_down * -30
        )

    bs.emitfx(
        position=node.position,
        velocity=node.velocity,
        count=50,
        scale=0.3,
        spread=0.1,
        chunk_type='spark'
    )

    bs.getsound('shieldHit').play(
        volume=time / 1000,
        position=node.position
    )

    for i in range(5):
        bs.timer(i * 0.01, impulse)


def enable() -> None:
    Spaz.dash_enabled = True
    Spaz.old_hook = Spaz.on_punch_release
    Spaz.on_punch_release = new_hook
