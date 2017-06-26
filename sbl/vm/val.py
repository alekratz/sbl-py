from enum import *


class ValType(Enum):
    INT = 'integer'
    IDENT = "identifier"
    CHAR = 'character'
    STRING = 'string'


class Val:
    def __init__(self, val, ty: ValType):
        self.val = val
        self.type = ty

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return f"Val({self.type.value} `{repr(self.val)}`)"

    def __eq__(self, other):
        return self.type == other.type and \
        (
            (self.val is not None and self.val == other.val) or
            self.val is None == other.val is None
        )
