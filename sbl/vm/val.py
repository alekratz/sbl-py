from enum import *


class ValType(Enum):
    INT = 'integer'
    IDENT = "identifier"
    CHAR = 'character'
    STRING = 'string'
    NIL = 'nil'
    BOOL = 'bool'
    STACK = 'stack'


class Val:
    def __init__(self, val, ty: ValType):
        assert isinstance(ty, ValType)
        self.val = val
        self.type = ty

    def is_const(self) -> bool:
        if self.type in [ValType.INT, ValType.CHAR, ValType.STRING, ValType.NIL, ValType.BOOL]:
            return True
        elif self.type is ValType.IDENT:
            return False
        else:
            assert self.type is ValType.STACK
            assert isinstance(self.val, list)
            return all(map(Val.is_const, self.val))

    def __str__(self):
        if self.type is ValType.STACK:
            return '[' + str(', '.join(map(str, self.val))) + ']'
        elif self.type is ValType.BOOL:
            return "T" if self.val else "F"
        else:
            return str(self.val)

    def __repr__(self):
        if self.type is ValType.NIL:
            return 'Nil'
        else:
            return f"Val({self.type.value} `{repr(self.val)}`)"

    def __eq__(self, other):
        return self.type == other.type and \
        (
            (self.val is not None and self.val == other.val) or
            self.val is None == other.val is None
        )
