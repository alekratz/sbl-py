from . token import *
from . ast import *


class Parser:
    def __init__(self, source: str):
        self.tokens = Tokenizer(source)
        self.curr = None
        self._next()

    def is_end(self) -> bool:
        return self.tokens.is_end()

    def parse(self) -> list:
        return self._expect_source()

    def _expect_source(self) -> List[FunDef]:
        funs = []
        while not self.is_end():
            funs += [self._expect_fundef()]
        return funs

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
            line = self._expect_line()
            end = copy(self.curr.range.start)
            lines += [line]
        return Block(Range(start, end), lines)

    def _expect_line(self) -> Line:
        if self._can_expect_any([TokenType.IDENT, TokenType.NUM, TokenType.SYM, TokenType.DOT]):
            return self._expect_action()
        elif self._can_expect(TokenType.BR):
            return self._expect_branch()
        else:
            types = [TokenType.IDENT, TokenType.NUM, TokenType.SYM, TokenType.BR, TokenType.DOT]
            raise ParseError(f"expected one of {', '.join(['`' + t.value + '`' for t in types])} token; "
                             f"instead got `{self.curr}` token", self.curr.range)

    def _expect_action(self) -> Action:
        start = copy(self.curr.range.start)
        pop = self._try_expect(TokenType.DOT)
        end = copy(self.curr.range.start)
        items = []
        while not self._try_expect(TokenType.SEMI):
            item = self._expect_item()
            if pop and type(item.val) is not str:
                raise ParseError(f"pop actions only accept identifiers, where a non-identifier (`{item}`) was found",
                                 item.range)
            end = copy(self.curr.range.start)
            items += [item]
        return Action(Range(start, end), items, pop)
    
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

    def _expect_item(self) -> Item:
        item = self._next_expect_any([TokenType.NUM, TokenType.IDENT, TokenType.SYM])
        return Item(item.range, item.payload)

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
                             f"instead got `{self.curr}` token", self.curr.range)

    def _next_expect(self, ty: TokenType):
        if self.curr.type == ty:
            return self._next()
        else:
            raise ParseError(f"expected `{ty.value}` token; instead got `{self.curr}` token", self.curr.range)

    def _next(self):
        """
        Gets the next token.
        """
        last = copy(self.curr)
        self.curr = self.tokens.next()
        while self.curr and self.curr.is_comment():
            self.curr = self.tokens.next()
        return last
