from enum import *

from sbl.syntax.ast import Val


class BCType(Enum):
    # Pushes the payload item to the stack.
    PUSH = auto()
    # Pops an item off the stack, into an identifier (or nothing at all).
    POP = auto()
    # Loads a stored value from memory and pushes its value onto the stack.
    LOAD = auto()
    # Jumps to a given label, given that the top item of the stack is zero.
    JMPZ = auto()
    # Jumps to a given label uncondiontally
    JMP = auto()
    # Calls a function.
    CALL = auto()
    # Returns from a function.
    RET = auto()


class BC:
    def __init__(self, code: BCType, meta=None, val: Val=None):
        if meta is None:
            meta = {}
        self.code = code
        self.val = val
        self.meta = meta

    def __str__(self):
        code_map = {
            BCType.PUSH: "PUSH",
            BCType.POP: "POP",
            BCType.LOAD: "LOAD",
            BCType.JMPZ: "JMPZ",
            BCType.JMP: "JMP",
            BCType.CALL: "CALL",
            BCType.RET: "RET",
        }
        if self.val:
            return f"{code_map[self.code].ljust(6)} {self.val}"
        else:
            return code_map[self.code].ljust(6)

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
