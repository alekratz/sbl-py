import string
from typing import *
from copy import copy

from common import *


"""
# Available tokens
comment = '#' .+ $

num = [1-9][0-9]*
    | '0' [xX] [0-9a-fA-F]+
    | '0' [bB] [01]+

ident = [A-z_][A-z\-_]*

dot = '.'

br = 'br'

el = 'el'

semi = ';'

lbrace = '{'

rbrace = '}'

sym = '!' | '@' | '$' | '%' | '^' | '&' | '*' | '-' | '+' | '/'

"""


syms = "!@$%^&*-+/"


class Token:
    COMMENT = 0
    NUM = 1
    IDENT = 2
    DOT = 3
    BR = 4
    EL = 5
    SEMI = 6
    LBRACE = 7
    RBRACE = 8
    SYM = 9

    def __init__(self, ty: int, rng: Range, payload: Any=None):
        self.type = ty
        self.range = rng
        self.payload = payload

    def is_comment(self) -> bool:
        return self.type == Token.COMMENT

    @staticmethod
    def comment(rng: Range):
        return Token(Token.COMMENT, rng)

    @staticmethod
    def dot(rng: Range):
        return Token(Token.DOT, rng)

    @staticmethod
    def semi(rng: Range):
        return Token(Token.SEMI, rng)

    @staticmethod
    def lbrace(rng: Range):
        return Token(Token.LBRACE, rng)

    @staticmethod
    def rbrace(rng: Range):
        return Token(Token.RBRACE, rng)

    @staticmethod
    def num(rng: Range, num: int):
        return Token(Token.NUM, rng, num)

    @staticmethod
    def ident(rng: Range, ident: str):
        return Token(Token.IDENT, rng, ident)

    @staticmethod
    def sym(rng: Range, sym: str):
        return Token(Token.SYM, rng, sym)

    def __str__(self):
        name = Token.type_str(self.type)
        if self.payload is not None:
            name += f" ({self.payload})"
        return name

    @staticmethod
    def type_str(ty: int):
        name_map = {
            Token.COMMENT: "Comment",
            Token.NUM: "Num",
            Token.IDENT: "Ident",
            Token.DOT: "Dot",
            Token.BR: "br",
            Token.EL: "el",
            Token.SEMI: "Semi",
            Token.LBRACE: "LBrace",
            Token.RBRACE: "RBrace",
            Token.SYM: "Sym",
        }
        assert ty in name_map
        return name_map[ty]


class Tokenizer:
    def __init__(self, source: str):
        self.source = source
        # current character
        self.curr_ch = None
        # pos looks at the position of the current character
        self.pos = Pos(-1, 0, 0)
        # next character
        self.next_ch = source[0] if len(source) > 0 else None
        # src_pos looks at the position of the next character
        self.src_pos = Pos(0, 0, 0)
        # this gets a character into the curr_ch slot
        self._adv()

    def next(self) -> Any:
        self._skip_ws()
        if self.curr_ch is None:
            return None
        elif self.curr_ch == '#':
            # comment
            start = copy(self.pos)
            while not self._is_src_end() and self.curr_ch != '\n':
                self._adv()
            end = copy(self.pos)
            return Token.comment(Range(start, end))
        elif self.curr_ch == '.':
            # dot
            start = end = copy(self.pos)
            self._adv()
            return Token.dot(Range(start, end))
        elif self.curr_ch == ';':
            # semicolon
            start = end = copy(self.pos)
            self._adv()
            return Token.semi(Range(start, end))
        elif self.curr_ch == '{':
            # lbrace
            start = end = copy(self.pos)
            self._adv()
            return Token.lbrace(Range(start, end))
        elif self.curr_ch == '}':
            # rbrace
            start = end = copy(self.pos)
            self._adv()
            return Token.rbrace(Range(start, end))
        elif self.curr_ch == '0' and self.next_ch in 'xX':
            # hex num
            start = copy(self.pos)
            end = copy(self.pos)
            # skip the prefix
            self._adv()
            self._adv()
            # expect at least one hex char
            if not self._adv_expect(string.hexdigits):
                raise ParseError(f"expected hex digit; instead got {self.curr_ch}", start)
            while self.curr_ch in string.hexdigits:
                end = copy(self.pos)
                self._adv()
            num = int(self.source[start.idx:end.idx + 1], 16)
            return Token.num(Range(start, end), num)
        elif self.curr_ch == '0' and self.next_ch in 'bB':
            # binary num
            start = copy(self.pos)
            end = copy(self.pos)
            # skip the prefix
            self._adv()
            self._adv()
            # expect at least one hex char
            if not self._adv_expect("01"):
                raise ParseError(f"expected binary digit; instead got {self.curr_ch}", start)
            while self.curr_ch in "01":
                end = copy(self.pos)
                self._adv()
            num = int(self.source[start.idx:end.idx + 1], 2)
            return Token.num(Range(start, end), num)
        elif self.curr_ch in string.digits:
            # num
            start = copy(self.pos)
            end = copy(self.pos)
            self._adv()
            while self.curr_ch in string.digits:
                end = copy(self.pos)
                self._adv()
            num = int(self.source[start.idx:end.idx + 1])
            return Token.num(Range(start, end), num)
        elif self.curr_ch in string.ascii_letters:
            keywords = {
                'br': Token.BR,
                'el': Token.EL,
            }
            # identifier, br/el keyword
            start = copy(self.pos)
            end = copy(self.pos)
            self._adv()
            while self.curr_ch in string.ascii_letters:
                end = copy(self.pos)
                self._adv()
            ident = self.source[start.idx:end.idx + 1]
            # choose keyword
            if ident in keywords:
                return Token(keywords[ident], Range(start, end))
            else:
                return Token.ident(Range(start, end), ident)
        elif self.curr_ch in syms:
            start = copy(self.pos)
            end = copy(self.pos)
            self._adv()
            while self.curr_ch in syms:
                end = copy(self.pos)
                self._adv()
            sym = self.source[start.idx:end.idx + 1]
            return Token.sym(Range(start, end), sym)
        else:
            raise ParseError(f"unexpected character reached: {repr(self.curr_ch)}", self.pos)

    def _adv_expect(self, charset) -> bool:
        if self.curr_ch not in charset:
            return False
        else:
            self._adv()
            return True

    """
    Advances the lexer forward one character, without skipping whitespace
    """
    def _adv(self):
        self.curr_ch = self.next_ch
        self.pos = copy(self.src_pos)
        if not self._is_src_end():
            self.src_pos.adv()
            if self._is_src_end():
                self.next_ch = None
            else:
                self.next_ch = self.source[self.src_pos.idx]
                # check the *previous* character
                if self.curr_ch == '\n':
                    self.src_pos.adv_line()
        # print(f"chars: {repr(self.curr_ch)}, {repr(self.next_ch)}")
    
    """
    Skips whitespace in the source text
    """
    def _skip_ws(self):
        while not self.is_end() and self.curr_ch in string.whitespace:
            self._adv()

    """
    Gets whether we're at the end of the source text, based on the `next_ch` character
    """
    def _is_src_end(self):
        return self.src_pos.idx >= len(self.source)

    """
    Gets whether we're at the end of the source text, based on the `next_ch` character
    """
    def is_end(self):
        return self.pos.idx >= len(self.source)
