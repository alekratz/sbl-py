class Pos:
    def __init__(self, col: int, line: int, idx: int):
        self.col = col
        self.line = line
        self.idx = idx

    def adv(self):
        self.col += 1
        self.idx += 1

    def adv_line(self, n=1):
        self.col = 0
        self.line += n

    def __str__(self):
        return f"{self.line+1}:{self.col+1}"


class Range:
    def __init__(self, start: Pos, end: Pos):
        self.start = start
        self.end = end

    def __str__(self):
        if self.start == self.end:
            return f"{self.start}"
        elif self.start.line == self.end.line:
            return f"{self.start.line+1}:{self.start.col+1}-{self.end.col+1}"
        else:
            return f"{self.start}-{self.end}"


class ParseError(Exception):
    def __init__(self, msg: str, rng: Range):
        super().__init__(f"at {rng}: {msg}")
        self.range = rng


class VMError(Exception):
    def __init__(self, msg, call_stack):
        super().__init__(msg)
        self.call_stack = call_stack


class CompileError(Exception):
    def __init__(self, msg: str, rng: Range):
        super().__init__(f"at {rng}: {msg}")
        self.range = rng


class FunError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class PreprocessError(Exception):
    def __init__(self, rng: Range, path: str):
        super().__init__(f"error in preprocessing {path}")
        self.rng = rng
        self.path = path