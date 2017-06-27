from .compile import *
from .funs import BUILTINS
from .val import Val, ValType


class VMState:
    def __init__(self, vm: 'VM'):
        self.stack = []
        self.call_stack = []
        self.vm = vm

    def load(self, name: str) -> Val:
        last = self.call_stack[-1]
        if name not in last.locals:
            raise VMError(f"unknown local `{name}`", self.vm, *self.current_loc())
        return last.load(name)

    def store(self, name: str, val: Val):
        last = self.call_stack[-1]
        last.store(name, val)

    def push(self, val: Val):
        self.stack += [val]

    def pop(self) -> Val:
        if len(self.stack) == 0:
            raise VMError(f"attempted to pop an empty stack", self.vm, *self.current_loc())
        return self.stack.pop()

    def push_fun(self, fun: Fun, callsite):
        self.call_stack += [FunState(fun, callsite)]

    def pop_fun(self) -> Fun:
        return self.call_stack.pop()

    def current_loc(self) -> (str, Range):
        """
        Attempts to find the location in source code using the current function state and its PC.
        :return:
        """
        fun_state = self.call_stack[-1]
        pc = fun_state.pc
        bc = fun_state.fun.bc
        curr_meta = bc[pc].meta
        return curr_meta['file'], curr_meta['where']
        

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
        self.state = VMState(self)

    def run(self):
        self._call('main', '<init>')

    def _call(self, fname: str, callsite):
        if fname not in self.funs and fname not in self.builtins:
            raise VMError(f"No such function: `{fname}`", self, *self.state.current_loc())
        if fname in self.builtins:
            # call builtin function
            try:
                self.builtins[fname](self.state)
            except VMError as e:
                raise ChainedError(f'builtin function `{fname}`', e)
            return
        # call user-defined function
        fun = self.funs[fname]
        self.state.push_fun(fun, callsite)
        fun_state = self._fun_state()
        while True:
            pc = fun_state.pc
            bc = fun.bc[pc]
            if bc.code == BCType.PUSH:
                self.state.push(bc.val)
                fun_state.pc += 1
            elif bc.code == BCType.POP:
                item = self.state.pop()
                if bc.val is not None:
                    self.state.store(bc.val.val, item)
                fun_state.pc += 1
            elif bc.code == BCType.POPN:
                if len(self.state.stack) < bc.val.val:
                    raise VMError(f"attempted to pop {bc.val.val} items off of a stack with only {len(self.state.stack)}"
                                  "items", self, bc.meta['file'], bc.meta['where'])
                self.state.stack = self.state.stack[0:len(self.state.stack) - bc.val.val]
                fun_state.pc += 1
            elif bc.code == BCType.JMPZ:
                assert bc.val.type is ValType.INT
                if len(self.state.stack) == 0:
                    raise VMError("could not compare to empty stack", self, bc.meta['file'], bc.meta['where'])
                tos = self.state.stack[-1]
                if not tos.val:
                    fun_state.pc = bc.val.val
                else:
                    fun_state.pc += 1
            elif bc.code == BCType.JMP:
                assert bc.val.type is ValType.INT
                fun_state.pc = bc.val.val
            elif bc.code == BCType.CALL:
                assert bc.val.type is ValType.IDENT
                self._call(bc.val.val, f"`{fun_state.name}` at {bc.meta['file']}:{bc.meta['where']}")
                fun_state.pc += 1
            elif bc.code == BCType.RET:
                break
            elif bc.code == BCType.LOAD:
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
