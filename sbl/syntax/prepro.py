# prepro.py
# Preprocesses an AST.
from .ast import *
from .parse import Parser
import os.path as path

def _path_find(import_path: List[str], filename: str):
    for d in import_path:
        if not path.isdir(d): continue
        fullpath = path.join(d, filename)
        if not path.isfile(fullpath): continue
        return fullpath

class Preprocess:
    def __init__(self, path: str, search_dirs: List[str], ast: Source, ignore=None):
        if ignore is None:
            ignore = []
        self.path = path
        self.search_dirs = search_dirs
        self.ast = ast
        self.ignore = ignore

    def preprocess(self) -> Source:
        src = []
        rm = []
        for top in self.ast:
            # skip non-imports
            if type(top) is not Import: continue
            # skip imports we've already visited
            inc_path = self.deduce_path(top.path)
            if inc_path is None:
                raise PreprocessImportError(top.range, top.path, self.search_dirs)
            # read and parse the source of the import file
            abs_include = path.abspath(inc_path)
            if abs_include in self.ignore: continue
            self.ignore += [abs_include]
            with open(inc_path) as fp:
                source = fp.read()
                try:
                    print("processing", inc_path)
                    parser = Parser(source, inc_path)
                    ast = parser.parse()
                    print(ast)
                    prepro = Preprocess(inc_path, self.search_dirs, ast, self.ignore)
                    src += prepro.preprocess()
                    src += prepro.ast
                except ParseError as e:
                    raise ChainedError(inc_path, e)
                except ChainedError as e:
                    raise ChainedError(inc_path, e)
            rm += [top]
        for r in rm:
            self.ast.remove(r)
        return src

    def deduce_path(self, name: str) -> Any:
        # if it's an absolute path that exists, just use that
        if path.isabs(name):
            return name
        inc_dir = path.dirname(name)
        for prefix in [inc_dir] + self.search_dirs:
            extd = path.join(prefix, name)
            if path.isfile(extd):
                return extd
        return None
