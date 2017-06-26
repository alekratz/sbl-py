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

    def __eq__(self, other):
        return isinstance(other, Item) and self.type == other.type and self.val == other.val


class Action:
    def __init__(self, rng: Range, items, pop=False):
        self.range = rng
        self.items = items
        self.pop = pop

    def __eq__(self, other):
        return isinstance(other, Action) and self.pop == other.pop and self.items == other.items


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

    def __eq__(self, other):
        return isinstance(other, Branch) and self.br_block == other.br_block and \
               (
                   (self.el_block is not None and self.el_block == other.el_block) or
                   self.el_block is None == other.el_block is None
                )


class Loop:
    def __init__(self, rng: Range, block: 'Block'):
        self.range = rng
        self.block = block

    def __eq__(self, other):
        return isinstance(other, Loop) and self.block == other.block


Line = Union[Action, Branch, Loop]


class Block:
    def __init__(self, rng: Range, lines: List[Line]):
        self.range = rng
        self.lines = lines

    def __iter__(self):
        for it in self.lines:
            yield it

    def __len__(self):
        return len(self.lines)

    def __eq__(self, other):
        if isinstance(other, Block):
            lines = other.lines
        else:
            lines = other
        if len(self.lines) != len(lines):
            return False
        for l1, l2 in zip(self.lines, lines):
            if l1 != l2: return False
        return True


class FunDef:
    def __init__(self, rng: Range, name: str, block: Block):
        self.range = rng
        self.name = name
        self.block = block

    def __eq__(self, other):
        return self.name == other.name and self.block == other.block


class Import:
    def __init__(self, rng: Range, path: str):
        self.range = rng
        self.path = path

    def __eq__(self, other):
        return self.path == other.path

TopLevel = Union[FunDef, Import]
Source = List[TopLevel]
