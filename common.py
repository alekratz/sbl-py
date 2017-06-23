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
    def __init__(self, msg: str, pos: Pos):
        super(ParseError, self).__init__(f"at {pos}: {msg}")


class VMError(Exception):
    def __init__(self, msg, call_stack):
        super(VMError, self).__init__(msg)
        self.call_stack = call_stack


class CompileError(Exception):
    def __init__(self, msg, pos):
        super(CompileError, self).__init__(f"at {pos}: {msg}")

