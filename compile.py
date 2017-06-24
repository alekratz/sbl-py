from parse import *
from typing import *
from common import *
from funs import BUILTINS


class BC:
    # Pushes the payload item to the stack.
    PUSH = 0
    # Pops an item off the stack, into an identifier (or nothing at all).
    POP = 1
    # Loads a stored value from memory and pushes its value onto the stack.
    LOAD = 2
    # Jumps to a given label, given that the top item of the stack is zero.
    JMPZ = 3
    # Jumps to a given label uncondiontally
    JMP = 4
    # Calls a function.
    CALL = 5
    # Returns from a function.
    RET = 6

    def __init__(self, code: int, meta=None, payload=None):
        if meta is None:
            meta = {}
        self.code = code
        self.payload = payload
        self.meta = meta

    def __str__(self):
        code_map = {
            BC.PUSH: "PUSH",
            BC.POP: "POP",
            BC.LOAD: "LOAD",
            BC.JMPZ: "JMPZ",
            BC.JMP: "JMP",
            BC.CALL: "CALL",
            BC.RET: "RET",
        }
        if self.payload:
            return f"{code_map[self.code].ljust(6)} {self.payload}"
        else:
            return code_map[self.code].ljust(6)

    @staticmethod
    def push(meta, item):
        return BC(BC.PUSH, meta, item)

    @staticmethod
    def pop(meta, item=None):
        return BC(BC.POP, meta, item)

    @staticmethod
    def jmpz(meta, item):
        return BC(BC.JMPZ, meta, item)

    @staticmethod
    def jmp(meta, item):
        return BC(BC.JMP, meta, item)

    @staticmethod
    def call(meta, item):
        return BC(BC.CALL, meta, item)

    @staticmethod
    def ret(meta):
        return BC(BC.RET, meta)

    @staticmethod
    def load(meta, item):
        return BC(BC.LOAD, meta, item)


class Fun:
    def __init__(self, name, bc, meta=None):
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
                                   f"{other_file} (other file)", f"{my_file}:{my_fun.meta['where']}")
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
        bc += [BC.ret(self._meta_with(where=fundef.range.end))]
        return Fun(name, bc, self._meta_with(where=fundef.range.start))

    def _compile_block(self, block: Block, jmp_offset=0) -> List[BC]:
        bc = []
        for line in block:
            if type(line) is Action:
                if line.pop:
                    # pops are allowed to not pop anything
                    if line.items:
                        for item in line.items:
                            bc += [BC.pop(self._meta_with(where=line.range), item.val)]
                    else:
                        bc += [BC.pop(self._meta_with(where=line.range))]
                else:
                    # split up the 'push' action by function names
                    for item in line.items:
                        if item.val in self.fun_names + list(self.builtins.keys()):
                            bc += [BC.call(self._meta_with(where=line.range), item.val)]
                        elif type(item.val) is str:
                            bc += [BC.load(self._meta_with(where=line.range), item.val)]
                        else:
                            bc += [BC.push(self._meta_with(where=item.range), item.val)]
            elif type(line) is Branch:
                start_addr = len(bc) + jmp_offset  # this is where we insert the first jump, later
                bc += [None]
                bc += self._compile_block(line.br_block, len(bc))
                if line.el_block:
                    end_addr = len(bc) + jmp_offset
                    bc += [None]
                    bc[start_addr] = BC.jmpz(self._meta_with(where=line.br_block.range), end_addr + 1)
                    bc += self._compile_block(line.el_block, len(bc))
                    bc[end_addr] = BC.jmp(self._meta_with(where=line.el_block.range), len(bc) + jmp_offset)
                else:
                    end_addr = len(bc) + jmp_offset
                    bc[start_addr] = BC.jmpz(self._meta_with(where=line.br_block.range), end_addr)
            else:
                assert False, f"line was neither an action nor a branch: {line}"
        return bc
