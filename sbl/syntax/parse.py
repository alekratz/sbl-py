from .ast import *
from .token import *


class Parser:
    def __init__(self, source: str, source_path: str):
        self.tokens = Tokenizer(source, source_path)
        self.source_path = source_path
        self.curr = None
        self._next()

    def is_end(self) -> bool:
        return self.tokens.is_end() and self.curr is None

    def parse(self) -> list:
        return self._expect_source()

    def _expect_source(self) -> List[FunDef]:
        funs = []
        while not self.is_end():
            funs += [self._expect_top_level()]
        return funs

    def _expect_top_level(self) -> TopLevel:
        if self._can_expect(TokenType.IMPORT):
            return self._expect_import()
        elif self._can_expect(TokenType.IDENT):
            return self._expect_fundef()
        else:
            raise ParseError(f"expected fundef or import; instead got {self.curr.type.value}", self.curr.range,
                             self.source_path)

    def _expect_import(self) -> Import:
        start = copy(self.curr.range.start)
        self._next_expect(TokenType.IMPORT)
        path = self._next_expect(TokenType.STRING)
        end = copy(self.curr.range.end)
        self._next_expect(TokenType.SEMI)
        return Import(Range(start, end), path.payload)

    def _expect_fundef(self) -> FunDef:
        start = copy(self.curr.range.start)
        name = self._expect_ident()
        block = self._expect_block()
        end = block.range.end
        return FunDef(Range(start, end), name, block)

    def _expect_block(self) -> Block:
        start = self.curr.range.start
        self._next_expect(TokenType.LBRACE)
        end = copy(self.curr.range.start)
        lines = []
        while not self._try_expect(TokenType.RBRACE):
            line = self._expect_stmt()
            end = copy(self.curr.range.start)
            lines += [line]
        return Block(Range(start, end), lines)

    def _expect_stmt(self) -> Stmt:

        types = [TokenType.IDENT, TokenType.NUM, TokenType.CHAR, TokenType.STRING, TokenType.SYM, TokenType.DOT]
        if self._can_expect_any(types):
            return self._expect_action()
        elif self._can_expect(TokenType.BR):
            return self._expect_branch()
        elif self._can_expect(TokenType.LOOP):
            return self._expect_loop()
        else:
            types += [TokenType.BR]
            raise ParseError(f"expected one of {', '.join(['`' + t.value + '`' for t in types])} token; "
                             f"instead got `{self.curr}` token", self.curr.range, self.source_path)

    def _expect_action(self) -> Action:
        if self._can_expect(TokenType.DOT):
            return self._expect_pop()
        else:
            return self._expect_push()

    def _expect_pop(self) -> PopAction:
        start = copy(self.curr.range.start)
        self._next_expect(TokenType.DOT)
        end = copy(self.curr.range.start)
        items = []
        while not self._try_expect(TokenType.SEMI):
            item = self._expect_item()
            if item.type not in [ItemType.IDENT, ItemType.INT]:
                raise ParseError(f"pop actions only accept identifiers and integers, where an invalid item"
                                 f"(`{item}`) was found", item.range, self.source_path)
            end = copy(self.curr.range.start)
            items += [item]
        return PopAction(Range(start, end), items)

    def _expect_push(self) -> PushAction:
        start = copy(self.curr.range.start)
        items = []
        while not self._try_expect(TokenType.SEMI):
            item = self._expect_item()
            items += [item]
        end = copy(self.curr.range.start)
        return PushAction(Range(start, end), items)

    def _expect_branch(self) -> Branch:
        start = copy(self.curr.range.start)
        self._next_expect(TokenType.BR)
        br_block = self._expect_block()
        end = br_block.range.end
        el_block = []
        if self._try_expect(TokenType.EL):
            el_block = self._expect_block()
            end = el_block.range.end
        return Branch(Range(start, end), br_block, el_block)

    def _expect_loop(self) -> Loop:
        start = copy(self.curr.range.start)
        self._next_expect(TokenType.LOOP)
        block = self._expect_block()
        end = block.range.end
        return Loop(Range(start, end), block)

    def _expect_item(self) -> Item:
        type_map = {
            TokenType.NUM: ItemType.INT,
            TokenType.IDENT: ItemType.IDENT,
            TokenType.SYM: ItemType.IDENT,
            TokenType.STRING: ItemType.STRING,
            TokenType.CHAR: ItemType.CHAR,
        }
        item = self._next_expect_any(list(type_map.keys()))
        return Item(item.range, item.payload, type_map[item.type])

    def _expect_ident(self) -> str:
        return self._next_expect(TokenType.IDENT).payload

    def _try_expect_any(self, types: List[TokenType]) -> bool:
        if self._can_expect_any(types):
            self._next()
            return True
        else:
            return False

    def _try_expect(self, ty: TokenType) -> bool:
        if self._can_expect(ty):
            self._next()
            return True
        else:
            return False

    def _can_expect_any(self, types: List[TokenType]) -> bool:
        return self.curr.type in types

    def _can_expect(self, ty: TokenType) -> bool:
        return self.curr.type == ty

    def _next_expect_any(self, types: List[TokenType]):
        if self.curr.type in types:
            return self._next()
        else:
            raise ParseError(f"expected one of {', '.join(['`' + t.value + '`' for t in types])} token; "
                             f"instead got `{self.curr}` token", self.curr.range, self.source_path)

    def _next_expect(self, ty: TokenType):
        if self.curr.type == ty:
            return self._next()
        else:
            raise ParseError(f"expected `{ty.value}` token; instead got `{self.curr}` token", self.curr.range,
                             self.source_path)

    def _next(self):
        """
        Gets the next token.
        """
        last = copy(self.curr)
        self.curr = self.tokens.next()
        while self.curr and self.curr.is_comment():
            self.curr = self.tokens.next()
        return last
