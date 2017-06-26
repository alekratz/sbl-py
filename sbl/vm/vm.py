from sbl.compile import *
from .funs import BUILTINS
from .val import Val, ValType


class VMState:
    def __init__(self):
        self.stack = []
        self.call_stack = []

    def load(self, name: str) -> Val:
        last = self.call_stack[-1]
        if name not in last.locals:
            raise VMError(f"unknown local `{name}`", self.call_stack)
        return last.load(name)

    def store(self, name: str, val: Val):
        last = self.call_stack[-1]
        last.store(name, val)

    def push(self, val: Val):
        self.stack += [val]

    def pop(self) -> Val:
        if len(self.stack) == 0:
            raise VMError(f"attempted to pop an empty stack", self.call_stack)
        return self.stack.pop()

    def push_fun(self, fun: Fun, callsite):
        self.call_stack += [FunState(fun, callsite)]

    def pop_fun(self) -> Fun:
        return self.call_stack.pop()
        

class FunState:
    def __init__(self, fun: Fun, callsite):
        self.name = fun.name
        self.fun = fun
        self.locals = {}
        self.pc = 0
        self.callsite = callsite

    def store(self, name: str, val: Val):
        self.locals[name] = val

    def load(self, name: str) -> Val:
        return self.locals[name]


class VM:
    def __init__(self, funs: FunTable, builtins=BUILTINS):
        self.funs = funs
        self.builtins = builtins
        self.state = VMState()

    def run(self):
        self._call('main', '<init>')

    def _call(self, fname: str, callsite):
        if fname not in self.funs and fname not in self.builtins:
            raise VMError(f"No such function: `{fname}`", self.state.call_stack)
        if fname in self.builtins:
            # call builtin function
            self.builtins[fname](self.state)
            return
        # call user-defined function
        fun = self.funs[fname]
        self.state.push_fun(fun, callsite)
        fun_state = self._fun_state()
        while True:
            pc = fun_state.pc
            bc = fun.bc[pc]
            if bc.code == BCType.PUSH:
                # printerr(f"PUSH {bc.val}")
                self.state.push(bc.val)
                fun_state.pc += 1
            elif bc.code == BCType.POP:
                item = self.state.pop()
                if bc.val is not None:
                    # printerr(f"POP {bc.val} [= {item}]")
                    self.state.store(bc.val.val, item)
                # else:
                    # printerr(f"POP")
                fun_state.pc += 1
            elif bc.code == BCType.JMPZ:
                assert bc.val.type is ValType.INT
                if len(self.state.stack) == 0:
                    raise VMError("could not compare to empty stack", self.state.call_stack)
                tos = self.state.stack[-1]
                if not tos.val:
                    # printerr(f"JUMP {bc.val}")
                    fun_state.pc = bc.val.val
                else:
                    fun_state.pc += 1
            elif bc.code == BCType.JMP:
                # printerr(f"JUMP {bc.val
                assert bc.val.type is ValType.INT
                fun_state.pc = bc.val.val
            elif bc.code == BCType.CALL:
                # printerr(f"CALL {bc.val} {self.state.stack}")
                assert bc.val.type is ValType.IDENT
                self._call(bc.val.val, f"`{fun_state.name}` at {bc.meta['file']}:{bc.meta['where']}")
                fun_state.pc += 1
            elif bc.code == BCType.RET:
                # printerr("RET")
                break
            elif bc.code == BCType.LOAD:
                # printerr(f"LOAD {bc.val}")
                assert bc.val.type is ValType.IDENT
                val = self.state.load(bc.val.val)
                self.state.push(val)
                fun_state.pc += 1
        self.state.pop_fun()

    def _fun_state(self):
        return self.state.call_stack[-1]

    def dump_funtable(self):
        for fun in self.funs:
            printerr(f"{fun}:")
            addr = 0
            for bc in self.funs[fun].bc:
                printerr("{:05}".format(addr), bc)
                addr += 1

    def dump_state(self):
        printerr("call stack:")

        for f in self.state.call_stack:
            printerr(f"{' ' * 4}{f.name} (defined at {f.fun.meta['file']}:{f.fun.meta['where']}) "
                     f"called from {f.callsite}")
            printerr(f"{' '*4}locals:")
            for l in f.locals:
                printerr(' ' * 8, f"{l} = {repr(f.locals[l])}")
        printerr("stack:")
        for s in reversed(self.state.stack):
            printerr(f"{' '*4}{repr(s)}")
