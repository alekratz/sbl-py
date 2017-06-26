from .bc import *
from .funs import BUILTINS
from sbl.syntax.parse import *


class Fun:
    def __init__(self, name: str, bc: List[BC], meta: Mapping[str, Any]=None):
        if meta is None:
            meta = {}
        self.name = name
        self.bc = bc
        self.meta = meta


class FunTable(dict):
    """
    A function table, with some optional metadata.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def merge(self, other):
        for name in other:
            if name in self:
                my_fun = self[name]
                my_file = my_fun.meta['file'] if 'file' in my_fun.meta else 'unknown'
                other_fun = other[name]
                other_file = other_fun.meta['file'] if 'file' in other_fun.meta else 'unknown'
                raise CompileError(f"duplicate function definition entries: `{name}` in {my_file} (this file) and "
                                   f"{other_file} (other file)", my_fun.meta['where'])
            else:
                self[name] = other[name]


class Compiler:
    def __init__(self, ast, meta=None):
        if meta is None:
            meta = {}
        self.ast = ast
        self.fun_names = []
        self.builtins = BUILTINS
        self.meta = meta
    
    def compile(self) -> FunTable:
        # First pass: get the names of each function
        self._build_funtable()
        funs = FunTable()
        for fun in self.ast:
            funs[fun.name] = self._compile_fun(fun)
        return funs

    def _meta_with(self, **kwargs):
        """
        Creates a new dict with metavariable data, in addition to the self.meta data.
        """
        meta = copy(self.meta)
        for k in kwargs:
            meta[k] = kwargs[k]
        return meta

    def _build_funtable(self):
        """
        Builds the internal list of functions. This does not change at run-time.
        """
        funs = {}
        # First pass: get names
        for fun in self.ast:
            assert type(fun) is FunDef
            if fun.name in self.fun_names:
                raise CompileError(f"function `{fun.name}` defined twice (first definition at "
                                   f"{funs[fun.name].range.start})", fun.range)
            self.fun_names += [fun.name]
            funs[fun.name] = fun

    def _compile_fun(self, fundef: FunDef):
        """
        Compiles a function from an AST FunDef
        """
        name = fundef.name
        bc = self._compile_block(fundef.block)
        bc += [BC.ret(self._meta_with(where=fundef.range))]
        return Fun(name, bc, self._meta_with(where=fundef.range))

    def _compile_block(self, block: Block, jmp_offset=0) -> List[BC]:
        bc = []
        for line in block:
            if type(line) is Action:
                if line.pop:
                    # pops are allowed to not pop anything
                    if line.items:
                        for item in line.items:
                            bc += [BC.pop(self._meta_with(where=line.range), item.to_val())]
                    else:
                        bc += [BC.pop(self._meta_with(where=line.range))]
                else:
                    # split up the 'push' action by function names
                    for item in line.items:
                        if item.val in self.fun_names + list(self.builtins.keys()):
                            bc += [BC.call(self._meta_with(where=line.range), item.to_val())]
                        elif item.type is ItemType.IDENT:
                            bc += [BC.load(self._meta_with(where=line.range), item.to_val())]
                        else:
                            bc += [BC.push(self._meta_with(where=item.range), item.to_val())]
            elif type(line) is Branch:
                start_addr = len(bc) + jmp_offset  # this is where we insert the first jump, later
                bc += [None]
                bc += self._compile_block(line.br_block, len(bc) + jmp_offset)
                if line.el_block:
                    end_addr = len(bc) + jmp_offset
                    bc += [None]
                    bc[start_addr] = BC.jmpz(self._meta_with(where=line.br_block.range), Val(end_addr + 1, ValType.INT))
                    bc += self._compile_block(line.el_block, len(bc))
                    bc[end_addr] = BC.jmp(self._meta_with(where=line.el_block.range), Val(len(bc) + jmp_offset,
                                                                                          ValType.INT))
                else:
                    end_addr = len(bc) + jmp_offset
                    bc[start_addr] = BC.jmpz(self._meta_with(where=line.br_block.range), Val(end_addr, ValType.INT))
            elif type(line) is Loop:
                start_addr = len(bc) + jmp_offset
                bc += [None]
                bc += self._compile_block(line.block, len(bc) + jmp_offset)
                bc += [BC.jmp(self._meta_with(where=line.block.range), Val(start_addr, ValType.INT))]
                end_addr = len(bc) + jmp_offset
                bc[start_addr] = BC.jmpz(self._meta_with(where=line.block.range), Val(end_addr, ValType.INT))
            else:
                assert False, f"line was neither an action nor a branch: {line}"
        return bc
