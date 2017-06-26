from enum import *

from .val import *


class BCType(Enum):
    # Pushes the payload item to the stack.
    PUSH = 'PUSH'
    # Pops an item off the stack, into an identifier (or nothing at all).
    POP = 'POP'
    # Loads a stored value from memory and pushes its value onto the stack.
    LOAD = 'LOAD'
    # Jumps to a given label, given that the top item of the stack is zero.
    JMPZ = 'JMPZ'
    # Jumps to a given label uncondiontally
    JMP = 'JMP'
    # Calls a function.
    CALL = 'CALL'
    # Returns from a function.
    RET = 'RET'

class BC:
    def __init__(self, code: BCType, meta=None, val: Val=None):
        if meta is None:
            meta = {}
        self.code = code
        self.val = val
        self.meta = meta

    def __str__(self):
        if self.val:
            return f"{self.code.value.ljust(6)} {repr(self.val)}"
        else:
            return self.code.value.ljust(6)

    def __repr__(self):
        return f"BC ({self.code.value} {repr(self.val)})"

    def __eq__(self, other):
        return isinstance(other, BC) and self.code == other.code and \
        (
            (self.val is not None and self.val == other.val) or
            self.val is None == other.val is None
        )

    @staticmethod
    def push(meta, val: Val) -> 'BC':
        return BC(BCType.PUSH, meta, val)

    @staticmethod
    def pop(meta, val: Val=None) -> 'BC':
        if val is None:
            return BC(BCType.POP, meta, val)
        else:
            return BC(BCType.POP, meta, val)

    @staticmethod
    def jmpz(meta, val: Val) -> 'BC':
        return BC(BCType.JMPZ, meta, val)

    @staticmethod
    def jmpnz(meta, val: Val) -> 'BC':
        return BC(BCType.JMPNZ, meta, val)

    @staticmethod
    def jmp(meta, val: Val) -> 'BC':
        return BC(BCType.JMP, meta, val)

    @staticmethod
    def call(meta, val: Val) -> 'BC':
        return BC(BCType.CALL, meta, val)

    @staticmethod
    def ret(meta) -> 'BC':
        return BC(BCType.RET, meta)

    @staticmethod
    def load(meta, val: Val) -> 'BC':
        return BC(BCType.LOAD, meta, val)
