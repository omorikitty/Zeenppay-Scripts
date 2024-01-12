import babase
import bascenev1 as bs


class PermissionEffect(object):
    def __init__(self, owner=None, tag: str = "", color=(1,1,1)):
        self.owner = owner


        math = bs.newnode('math', 
            owner=self.owner,
            attrs={
                'input1': (0.0, 1.4, 0.0),
                'operation': 'add'
            })

        self.owner.connectattr('position_center', math, 'input2')


        self.text = bs.newnode('text',
                               owner=self.owner,
                               attrs={
                                   'text': tag,
                                   'in_world': True,
                                   'shadow': 1.0,
                                   'flatness': 1.0,
                                   'color': tuple(color),
                                   'scale': 0.01,
                                   'h_align': 'center'
                               })
        math.connectattr('output', self.text, 'position')

