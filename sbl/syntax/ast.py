from sbl.common import *
from sbl.vm.val import *
from sbl.syntax.token import TokenType


class ItemType(Enum):
    INT = 'integer'
    IDENT = "identifier"
    CHAR = 'character'
    STRING = 'string'
    BOOL = 'boolean'
    STACK = 'stack'
    NIL = 'nil'

    def to_val_type(self) -> ValType:
        mapping = {
            ItemType.INT: ValType.INT,
            ItemType.IDENT: ValType.IDENT,
            ItemType.CHAR: ValType.CHAR,
            ItemType.STRING: ValType.STRING,
            ItemType.NIL: ValType.NIL,
            ItemType.BOOL: ValType.BOOL,
            ItemType.STACK: ValType.STACK,
        }
        return mapping[self]


class AST(metaclass=ABCMeta):
    def __init__(self, range: Range):
        self.range = range

    @staticmethod
    @abstractmethod
    def lookaheads() -> List[TokenType]:
        pass


class Item(AST):
    def __init__(self, rng: Range, val, ty: ItemType):
        super().__init__(rng)
        self.val = val
        self.type = ty

    def is_const(self) -> bool:
        if self.type in [ItemType.INT, ItemType.CHAR, ItemType.STRING, ItemType.NIL, ItemType.BOOL]:
            return True
        elif self.type is ItemType.IDENT:
            return False
        else:
            assert self.type is ItemType.STACK, f'for some reason got {self.type}'
            assert isinstance(self.val, list)
            return all(map(Item.is_const, self.val))

    def to_val(self) -> Val:
        assert (self.type is ItemType.STACK and self.is_const()) or self.type is not ItemType.STACK
        if self.type is ItemType.STACK:
            # handle stacks specially
            return Val(list(map(Item.to_val, self.val)), self.type.to_val_type())
        else:
            return Val(self.val, self.type.to_val_type())

    def __str__(self):
        return f"{self.type.value} {repr(self.val)}"

    def __repr__(self):
        return f"Item({self})"

    def __eq__(self, other):
        return isinstance(other, Item) and self.type == other.type and self.val == other.val

    @staticmethod
    def lookaheads() -> List[TokenType]:
        return [TokenType.IDENT, TokenType.NUM, TokenType.CHAR, TokenType.STRING, TokenType.NIL, TokenType.T,
                TokenType.F, TokenType.LBRACK]


class StackAction(AST):
    def __init__(self, rng: Range, item, pop: bool):
        super().__init__(rng)
        self.item = item
        self.pop = pop

    def __eq__(self, other):
        return isinstance(other, StackAction) and self.item == other.item and self.pop == other.pop

    def __str__(self):
        if self.pop:
            return f". ({repr(self.item)})"
        else:
            return f"({repr(self.item)})"

    def __repr__(self):
        return f"StackAction({self}))"

    @staticmethod
    def lookaheads() -> List[TokenType]:
        return Item.lookaheads() + [TokenType.DOT]


class StackStmt(AST):
    def __init__(self, rng: Range, items: List[StackAction]):
        super().__init__(rng)
        self.items = items

    def __eq__(self, other):
        return isinstance(other, StackStmt) and self.items == other.items

    def __str__(self):
        return f"[{', '.join(map(str, self.items))}]"

    def __repr__(self):
        return f"StackStmt ([{', '.join(map(str, self.items))}])"

    @staticmethod
    def lookaheads() -> List[TokenType]:
        return StackAction.lookaheads() + [TokenType.SEMI]


class Branch(AST):
    """
    A branch statement. A branch may optionally have a trailing "el" block as
    well.
    :br: the list of lines held by the br block.
    :el: the list of lines held by the el block.
    """
    def __init__(self, rng: Range, br_block: 'Block', el_block: 'Block'):
        super().__init__(rng)
        self.br_block = br_block
        self.el_block = el_block

    def __eq__(self, other):
        return isinstance(other, Branch) and self.br_block == other.br_block and \
               (
                   (self.el_block is not None and self.el_block == other.el_block) or
                   self.el_block is None == other.el_block is None
               )

    @staticmethod
    def lookaheads() -> List[TokenType]:
        return [TokenType.BR]


class Loop(AST):
    def __init__(self, rng: Range, block: 'Block'):
        super().__init__(rng)
        self.block = block

    def __eq__(self, other):
        return isinstance(other, Loop) and self.block == other.block

    @staticmethod
    def lookaheads() -> List[TokenType]:
        return [TokenType.LOOP]


Stmt = Union[StackStmt, Branch, Loop]


class Block(AST):
    def __init__(self, rng: Range, lines: List[Stmt]):
        super().__init__(rng)
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

    @staticmethod
    def lookaheads() -> List[TokenType]:
        return [TokenType.LBRACE]


class FunDef(AST):
    def __init__(self, rng: Range, name: str, block: Block):
        super().__init__(rng)
        self.name = name
        self.block = block

    def __eq__(self, other):
        return self.name == other.name and self.block == other.block

    @staticmethod
    def lookaheads() -> List[TokenType]:
        return [TokenType.IDENT]

class Import(AST):
    def __init__(self, rng: Range, path: str):
        super().__init__(rng)
        self.path = path

    def __eq__(self, other):
        return self.path == other.path

    @staticmethod
    def lookaheads() -> List[TokenType]:
        return [TokenType.IMPORT]

TopLevel = Union[FunDef, Import]
Source = List[TopLevel]
