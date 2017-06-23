#!/usr/bin/env python3
# A stack-based language written during internet downtime for funsies

from common import *
from parse import *
from vm import *

from argparse import ArgumentParser

import sys

# TODO
# * Prettier errors (including source text)
# * Merging together SBL files' compiled bytecode
# * Loops
# * Types outside of numbers
# * ???

def parse_args():
    parser = ArgumentParser(description="Runs SBL code.")
    parser.add_argument('files', metavar='FILE', type=str, nargs='+',
            help='Files to run')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    for fname in args.files:
        source_name = fname
        with open(fname) as fp:
            source = fp.read()
        try:
            # build the compiler parts and compile
            parser = Parser(source)
            compiler = Compiler(parser.parse(), { 'file': source_name })
            vm = VM(compiler.compile())
            vm.run()
        except ParseError as e:
            print(f"Parse error in {source_name}:")
            print(f"{' ' * 4}{e}")
        except CompileError as e:
            print(f"Compilation error in {source_name}:")
            print(f"{' ' * 4}{e}")
        except VMError as e:
            print(f"Runtime error in {source_name}:")
            print(f"{' ' * 4}{e}")
            print("call stack:")
            for f in e.call_stack:
                print(f"{' ' * 4}{f.name} (defined at {f.fun.meta['file']}:{f.fun.meta['where']}) called from {f.callsite}")

