from sbl.syntax.ast import *
from sbl.syntax.token import *


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
        if self._can_expect_any(Import.lookaheads()):
            return self._expect_import()
        elif self._can_expect_any(FunDef.lookaheads()):
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
        if self._can_expect_any(StackStmt.lookaheads()):
            return self._expect_action()
        elif self._can_expect_any(Branch.lookaheads()):
            return self._expect_branch()
        elif self._can_expect_any(Loop.lookaheads()):
            return self._expect_loop()
        else:
            types = StackStmt.lookaheads() + Branch.lookaheads() + Loop.lookaheads()
            raise ParseError(f"expected one of {', '.join(['`' + t.value + '`' for t in types])} token; "
                             f"instead got `{self.curr}` token", self.curr.range, self.source_path)

    def _expect_action(self) -> StackStmt:
        start = copy(self.curr.range.start)
        items = []
        end = copy(self.curr.range.end)
        while not self._try_expect(TokenType.SEMI):
            if self._can_expect(TokenType.DOT):
                items += [self._expect_pop()]
            else:
                items += [self._expect_push()]
            end = copy(self.curr.range.end)
        return StackStmt(Range(start, end), items)

    def _expect_pop(self) -> StackAction:
        start = copy(self.curr.range.start)
        self._next_expect(TokenType.DOT)
        end = copy(self.curr.range.end)
        item = self._expect_item()
        if item.type not in [ItemType.IDENT, ItemType.NIL, ItemType.INT]:
            raise ParseError('pop targets must be one of `ident`, `nil`, or `num` tokens',
                             item.range, self.source_path)
        return StackAction(Range(start, end), item, True)

    def _expect_push(self) -> StackAction:
        start = copy(self.curr.range.start)
        end = copy(self.curr.range.end)
        item = self._expect_item()
        return StackAction(Range(start, end), item, False)

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
        # stack literals are special, so try to match those first
        if self._can_expect(TokenType.LBRACK):
            return self._expect_stack()
        type_map = {
            TokenType.NUM: ItemType.INT,
            TokenType.IDENT: ItemType.IDENT,
            TokenType.STRING: ItemType.STRING,
            TokenType.CHAR: ItemType.CHAR,
            TokenType.NIL: ItemType.NIL,
            TokenType.T: ItemType.BOOL,
            TokenType.F: ItemType.BOOL,
        }
        item = self._next_expect_any(list(type_map.keys()))
        if item.type is TokenType.T:
            return Item(item.range, True, type_map[item.type])
        elif item.type is TokenType.F:
            return Item(item.range, False, type_map[item.type])
        else:
            return Item(item.range, item.payload, type_map[item.type])

    def _expect_stack(self) -> Item:
        start = copy(self.curr.range.start)
        self._next_expect(TokenType.LBRACK)
        end = copy(self.curr.range.start)
        items = []
        while not self._try_expect(TokenType.RBRACK):
            items += [self._expect_item()]
            end = copy(self.curr.range.end)
        return Item(Range(start, end), items, ItemType.STACK)

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

    def _next_expect_any(self, types: List[TokenType]) -> Token:
        if self.curr.type in types:
            return self._next()
        else:
            raise ParseError(f"expected one of {', '.join(['`' + t.value + '`' for t in types])} token; "
                             f"instead got `{self.curr}` token", self.curr.range, self.source_path)

    def _next_expect(self, ty: TokenType) -> Token:
        if self.curr.type == ty:
            return self._next()
        else:
            raise ParseError(f"expected `{ty.value}` token; instead got `{self.curr}` token", self.curr.range,
                             self.source_path)

    def _next(self) -> Token:
        """
        Gets the next token.
        """
        last = copy(self.curr)
        self.curr = self.tokens.next()
        while self.curr and self.curr.is_comment():
            self.curr = self.tokens.next()
        return last
