from token import *
from typing import *
from common import *
from copy import copy

"""
# Stack-based language grammar

source = fundef*

fundef = <ident> block

block = '{' line* '}'

line = action ';'
     | branch

action = '.' ident*
       | item*

branch = <br> block
       | <br> block <el> block

item = <ident>
     | <num>
     | <sym>

"""

class Item:
    def __init__(self, range, val):
        self.range = range
        self.val = val

    def __repr__(self):
        return repr(self.val)

class Action:
    def __init__(self, range, items, pop=False):
        self.range = range
        self.items = items
        self.pop = pop

class Branch:
    """
    A branch statement. A branch may optionally have a trailing "el" block as
    well.
    :br: the list of lines held by the br block.
    :el: the list of lines held by the el block.
    """
    def __init__(self, range, br_block, el_block):
        self.range = range
        self.br_block = br_block
        self.el_block = el_block

Line = Union[Action, Branch]

class Block:
    def __init__(self, range, lines: List[Line]):
        self.range = range
        self.lines = lines

    def __iter__(self):
        for it in self.lines:
            yield it


class FunDef:
    def __init__(self, range, name: str, block: Block):
        self.range = range
        self.name = name
        self.block = block


Source = List[FunDef]


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
        self._next_expect(Token.LBRACE)
        end = copy(self.curr.range.start)
        lines = []
        while not self._try_expect(Token.RBRACE):
            line = self._expect_line()
            end = copy(self.curr.range.start)
            lines += [line]
        return Block(Range(start, end), lines)

    def _expect_line(self) -> Line:
        if self._can_expect_any([Token.IDENT, Token.NUM, Token.SYM, Token.DOT]):
            return self._expect_action()
        elif self._can_expect(Token.BR):
            return self._expect_branch()
        else:
            types = [Token.IDENT, Token.NUM, Token.SYM, Token.BR, Token.DOT]
            raise ParseError(f"expected one of {', '.join(['`' + Token.type_str(t) + '`' for t in types])} token; instead got `{self.curr}` token", self.curr.range)

    def _expect_action(self) -> Action:
        start = copy(self.curr.range.start)
        pop = self._try_expect(Token.DOT)
        end = copy(self.curr.range.start)
        items = []
        while not self._try_expect(Token.SEMI):
            item = self._expect_item()
            if pop and type(item.val) is not str:
                raise ParseError(f"pop actions only accept identifiers, where a non-identifier (`{item}`) was found", item.range)
            end = copy(self.curr.range.start)
            items += [item]
        return Action(Range(start, end), items, pop)
    
    def _expect_branch(self) -> Branch:
        start = copy(self.curr.range.start)
        self._next_expect(Token.BR)
        br_block = self._expect_block()
        end = br_block.range.end
        el_block = []
        if self._try_expect(Token.EL):
            el_block = self._expect_block()
            end = el_block.range.end
        return Branch(Range(start, end), br_block, el_block)

    def _expect_item(self) -> Item:
        item = self._next_expect_any([Token.NUM, Token.IDENT, Token.SYM])
        return Item(item.range, item.payload)

    def _expect_ident(self) -> str:
        return self._next_expect(Token.IDENT).payload

    def _try_expect_any(self, types: List[int]) -> bool:
        if self._can_expect_any(types):
            self._next()
            return True
        else:
            return False

    def _try_expect(self, type: int) -> bool:
        if self._can_expect(type):
            self._next()
            return True
        else:
            return False

    def _can_expect_any(self, types: List[int]) -> bool:
        return self.curr.type in types

    def _can_expect(self, type: int) -> bool:
        return self.curr.type == type

    def _next_expect_any(self, types: List[int]):
        if self.curr.type in types:
            return self._next()
        else:
            raise ParseError(f"expected one of {', '.join(['`' + Token.type_str(t) + '`' for t in types])} token; instead got `{self.curr}` token", self.curr.range)

    def _next_expect(self, type: int):
        if self.curr.type == type:
            return self._next()
        else:
            raise ParseError(f"expected `{Token.type_str(type)}` token; instead got `{self.curr}` token", self.curr.range)

    def _next(self):
        """
        Gets the next token.
        """
        last = copy(self.curr)
        self.curr = self.tokens.next()
        while self.curr and self.curr.is_comment():
            self.curr = self.tokens.next()
        return last
