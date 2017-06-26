#!/usr/bin/env python3
# A stack-based language written during internet downtime for funsies

import sys
import os
from argparse import ArgumentParser
import argparse

from . vm.vm import *
from . syntax.prepro import *
from . common import printerr


# Ideas
# * elbr - elif-style branch constructs
# * Labels + goto?

def parse_args():
    parser = ArgumentParser(description="Runs SBL code.")
    # TODO: -c option like python has
    parser.add_argument('-v', '--verbose', action='count', help='Show detailed information')
    parser.add_argument('file', metavar='FILE', type=str, help='File to run')
    parser.add_argument('argv', metavar='ARGV', nargs=argparse.REMAINDER, help='Program arguments')
    return parser.parse_args()


def main():
    IMPORT_PATH = 'SBL_PATH'
    error = False

    search_dirs = os.environ[IMPORT_PATH].split(':') if IMPORT_PATH in os.environ else []
    args = parse_args()
    fname = args.file
    verbose = args.verbose
    source_name = fname
    vm = None
    # try to get the source text
    try:
        with open(fname) as fp:
            source = fp.read()
    except FileNotFoundError:
        printerr(f"File not found: `{fname}`")
        sys.exit(1)
    # build the compiler parts and compile
    try:
        # parse
        parser = Parser(source, fname)
        ast = parser.parse()
        # preprocess (get imports)
        prepro = Preprocess(fname, search_dirs, ast)
        ast += prepro.preprocess()
        # compile to bytecode
        compiler = Compiler(ast, { 'file': source_name })
        fun_table = compiler.compile()
        # empty programs are valid; just don't run anything
        if len(fun_table) > 0:
            vm = VM(fun_table)
            vm.run()
    except PreprocessImportError as e:
        printerr(f"Preprocess error in {fname}:")
        printerr(f"{' ' * 4}{e.path}: {e}")
        if verbose:
            printerr(f"{' ' * 4}Path:")
            for dirname in e.import_path:
                printerr(f"{' ' * 8}{repr(dirname)}")
        error = True
    except ChainedError as e:
        printerr(f"Preprocess error caused by {fname}:")
        e.printerr()
        error = True
    except ParseError as e:
        e.printerr()
        error = True
    except CompileError as e:
        printerr(f"Compilation error in {source_name}:")
        printerr(f"{' ' * 4}{e}")
        for line in underline_source(source, e.range):
            printerr(f"{' ' * 8}{line}")
        error = True
    except VMError as e:
        assert vm is not None
        printerr(f"Runtime error in {source_name}:")
        printerr(f"{' ' * 4}{e}")
        if verbose:
            printerr("VM state:")
            vm.dump_state()
        else:
            printerr("call stack:")
            for f in e.call_stack:
                printerr(f"{' ' * 4}{f.name} (defined at {f.fun.meta['file']}:{f.fun.meta['where']}) "
                         f"called from {f.callsite}")
        if verbose >= 2:
            printerr("VM funtable:")
            vm.dump_funtable()
        error = True
    if error:
        sys.exit(1)


if __name__ == '__main__':
    main()