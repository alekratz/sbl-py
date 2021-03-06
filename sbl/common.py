from typing import *
from sys import stderr
from abc import ABCMeta, abstractmethod


def printerr(*args, **kwargs):
    print(*args, **kwargs, file=stderr)


def underline_source(source: str, rng: 'Range'):
    MAX_LINE_LEN = 70
    line_diff = rng.end.line - rng.start.line
    lines = source.split('\n')
    # TODO : multi-line underlining
    if line_diff == 0:
        # same line
        sz = rng.end.col - rng.start.col
    else:
        sz = len(lines[rng.start.line]) - rng.start.col
    sz += 1
    padded_line = lines[rng.start.line]
    line = padded_line.lstrip()
    if len(line) > MAX_LINE_LEN:
        line = line[0:MAX_LINE_LEN] + ' ...'
    offset = rng.start.col - (len(padded_line) - len(line))
    return [
        line,
        " " * offset + "^" * sz,
    ]


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


class PrintErr(Exception, metaclass=ABCMeta):
    @abstractmethod
    def printerr(self, verbose=0):
        pass


class ChainedError(PrintErr):
    """
    A generic error chain.
    """
    def __init__(self, message: str, err: PrintErr):
        super().__init__(f"{' '*4}in error caused by {message}")
        self.err = err

    def printerr(self, verbose=0):
        printerr(self)
        self.err.printerr(verbose=verbose)


class ParseError(PrintErr):
    def __init__(self, msg: str, rng: Range, path: str):
        super().__init__(f"{rng}: {msg}")
        self.range = rng
        self.path = path

    def printerr(self, verbose=0):
        printerr(f"Parse error in {self.path}:")
        with open(self.path) as fp:
            source = fp.read()
        printerr(f"{' ' * 4}{self}")
        for line in underline_source(source, self.range):
            printerr(f"{' ' * 8}{line}")


class VMError(PrintErr):
    def __init__(self, msg, vm, source_file: str, source_range: Range):
        super().__init__(msg)
        self.vm = vm
        self.source_file = source_file
        self.source_range = source_range

    def printerr(self, verbose=0):
        printerr(f"Runtime error in {self.source_file}:{self.source_range}")
        printerr(f"{' ' * 4}{self}")
        if verbose:
            printerr("VM state:")
            self.vm.dump_state()
        else:
            printerr("call stack:")
            for f in self.vm.state.call_stack:
                printerr(f"{' ' * 4}{f.name} (defined at {f.fun.meta['file']}:{f.fun.meta['where']}) "
                         f"called from {f.callsite}")
        if verbose >= 2:
            printerr("VM funtable:")
            self.vm.dump_funtable()


class CompileError(Exception):
    def __init__(self, msg: str, rng: Range):
        super().__init__(f"at {rng}: {msg}")
        self.range = rng


class FunError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class PreprocessImportError(Exception):
    """
    An error where a file failed to import.
    """
    def __init__(self, rng: Range, path: str, import_path: List[str]):
        super().__init__("file not found")
        self.rng = rng
        self.import_path = import_path
        self.path = path