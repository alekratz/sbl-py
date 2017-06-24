from typing import *


class Item:
    def __init__(self, rng, val):
        self.range = rng
        self.val = val

    def __repr__(self):
        return repr(self.val)


class Action:
    def __init__(self, rng, items, pop=False):
        self.range = rng
        self.items = items
        self.pop = pop


class Branch:
    """
    A branch statement. A branch may optionally have a trailing "el" block as
    well.
    :br: the list of lines held by the br block.
    :el: the list of lines held by the el block.
    """
    def __init__(self, rng, br_block, el_block):
        self.range = rng
        self.br_block = br_block
        self.el_block = el_block

Line = Union[Action, Branch]


class Block:
    def __init__(self, rng, lines: List[Line]):
        self.range = rng
        self.lines = lines

    def __iter__(self):
        for it in self.lines:
            yield it


class FunDef:
    def __init__(self, rng, name: str, block: Block):
        self.range = rng
        self.name = name
        self.block = block


Source = List[FunDef]