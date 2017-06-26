from sbl.common import *
from sbl.vm.val import Val
from typing import *
from . type import *


class Item:
    def __init__(self, rng: Range, val, ty: ItemType):
        self.range = rng
        self.val = val
        self.type = ty

    def to_val(self) -> Val:
        return Val(self.val, self.type)

    def __str__(self):
        return f"{self.type.value} ({repr(self.val)})"

    def __repr__(self):
        return f"Item({self}))"


class Action:
    def __init__(self, rng: Range, items, pop=False):
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
    def __init__(self, rng: Range, br_block: 'Block', el_block: 'Block'):
        self.range = rng
        self.br_block = br_block
        self.el_block = el_block


Line = Union[Action, Branch, 'Loop']


class Block:
    def __init__(self, rng: Range, lines: List[Line]):
        self.range = rng
        self.lines = lines

    def __iter__(self):
        for it in self.lines:
            yield it

    def __len__(self):
        return len(self.lines)


class Loop:
    def __init__(self, rng: Range, block: Block):
        self.range = rng
        self.block = block


class FunDef:
    def __init__(self, rng: Range, name: str, block: Block):
        self.range = rng
        self.name = name
        self.block = block


class Import:
    def __init__(self, rng: Range, path: str):
        self.range = rng
        self.path = path

TopLevel = Union[FunDef, Import]
Source = List[TopLevel]
