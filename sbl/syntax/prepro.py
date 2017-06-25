# prepro.py
# Preprocesses an AST.
from .ast import *
from .parse import Parser
import os.path as path

class Preprocess:
    def __init__(self, ast: Source, ignore=None):
        if ignore is None:
            ignore = []
        self.ast = ast
        self.ignore = ignore

    def preprocess(self) -> Source:
        src = []
        rm = []
        for top in self.ast:
            # skip non-imports
            if type(top) is not Import: continue
            if top.path in self.ignore: continue
            if not path.exists(top.path):
                raise PreprocessError(top.range, top.path)
            # read and parse the source of the import file
            self.ignore += [top.path]
            with open(top.path) as fp:
                source = fp.read()
                parser = Parser(source)
                ast = parser.parse()
                prepro = Preprocess(ast, self.ignore)
                src += prepro.preprocess() + ast
            rm += [top]
        for r in rm:
            self.ast.remove(r)
        return src
