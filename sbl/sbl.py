#!/usr/bin/env python3
# A stack-based language written during internet downtime for funsies

import sys
from argparse import ArgumentParser

from . vm.vm import *


# TODO
# * Loops
# * Types outside of numbers
# * Labels + goto?
# * File imports

def parse_args():
    parser = ArgumentParser(description="Runs SBL code.")
    parser.add_argument('files', metavar='FILE', type=str, nargs='+',
            help='Files to run')
    return parser.parse_args()

def underline_source(source: str, rng: Range):
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

def main():
    args = parse_args()
    error = False

    fun_table = FunTable()
    for fname in args.files:
        source_name = fname
        with open(fname) as fp:
            source = fp.read()
        try:
            # build the compiler parts and compile
            parser = Parser(source)
            compiler = Compiler(parser.parse(), { 'file': source_name })
            fun_table.merge(compiler.compile())
        except ParseError as e:
            print(f"Parse error in {source_name}:")
            print(f"{' ' * 4}{e}")
            for line in underline_source(source, e.range):
                print(f"{' ' * 8}{line}")
            error = True
        except CompileError as e:
            print(f"Compilation error in {source_name}:")
            print(f"{' ' * 4}{e}")
            for line in underline_source(source, e.range):
                print(f"{' ' * 8}{line}")
            error = True
    if error:
        sys.exit(1)
    if len(fun_table) == 0:
        sys.exit(0)
    vm = VM(fun_table)
    try:
        vm.run()
    except VMError as e:
            print(f"Runtime error in {source_name}:")
            print(f"{' ' * 4}{e}")
            print("call stack:")
            for f in e.call_stack:
                print(f"{' ' * 4}{f.name} (defined at {f.fun.meta['file']}:{f.fun.meta['where']}) "
                      f"called from {f.callsite}")
