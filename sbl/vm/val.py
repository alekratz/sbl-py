from sbl.syntax.ast import ItemType


ValType = ItemType

class Val:
    def __init__(self, val, ty: ValType):
        self.val = val
        self.type = ty

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return f"Val({self.type} `{repr(self.val)}`"
