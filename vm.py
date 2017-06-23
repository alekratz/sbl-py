from compile import *
from parse import *
from typing import *
from funs import BUILTINS


class VMState:
    def __init__(self):
        self.stack = []
        self.call_stack = []

    def load(self, name):
        last = self.call_stack[-1]
        if name not in last.locals:
            raise VMError(f"unknown local `{name}`", self.call_stack)
        return last.load(name)

    def store(self, name, val):
        last = self.call_stack[-1]
        last.store(name, val)

    def push(self, item):
        self.stack += [item]

    def pop(self):
        if len(self.stack) == 0:
            raise VMError(f"attempted to pop an empty stack", self.call_stack)
        return self.stack.pop()

    def push_fun(self, fun: Fun, callsite):
        self.call_stack += [FunState(fun, callsite)]

    def pop_fun(self) -> Fun:
        return self.call_stack.pop()
        

class FunState:
    def __init__(self, fun, callsite):
        self.name = fun.name
        self.fun = fun
        self.locals = {}
        self.pc = 0
        self.callsite = callsite

    def store(self, name, item):
        self.locals[name] = item

    def load(self, name):
        return self.locals[name]


"""
Virtual machine class.
"""
class VM:
    def __init__(self, funs, builtins=BUILTINS):
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
            if bc.code == BC.PUSH:
                #print(f"PUSH {bc.payload}")
                self.state.push(bc.payload)
                fun_state.pc += 1
            elif bc.code == BC.POP:
                item = self.state.pop()
                if bc.payload is not None:
                    #print(f"POP {bc.payload} [= {item}]")
                    self.state.store(bc.payload, item)
                #else:
                    #print(f"POP")
                fun_state.pc += 1
            elif bc.code == BC.JMPZ:
                tos = self.state.stack[-1]
                if tos == 0:
                    #print(f"JUMP {bc.payload}")
                    fun_state.pc = bc.payload
                else:
                    fun_state.pc += 1
            elif bc.code == BC.JMP:
                #print(f"JUMP {bc.payload}")
                fun_state.pc = bc.payload
            elif bc.code == BC.CALL:
                #print(f"CALL {bc.payload} {self.state.stack}")
                self._call(bc.payload, f"`{fun_state.name}` at {bc.meta['file']}:{bc.meta['where']}")
                fun_state.pc += 1
            elif bc.code == BC.RET:
                #print("RET")
                break
            elif bc.code == BC.LOAD:
                #print(f"LOAD {bc.payload}")
                val = self.state.load(bc.payload)
                self.state.push(val)
                fun_state.pc += 1
        self.state.pop_fun()

    def _fun_state(self):
        return self.state.call_stack[-1]

    def dump_funtable(self):
        for fun in self.funs:
            print(f"{fun}:")
            addr = 0
            for bc in self.funs[fun].bc:
                print("{:05}".format(addr), bc)
                addr += 1
            print()

    def dump_state(self):
        print("call stack:")
        for f in reversed(self.state.call_stack):
            print(' ' * 4, f"{f.name}")
            for l in f.locals:
                print(' ' * 8, f"{l}: {f.locals[l]}")
        print()
        print("stack:")
        for s in reversed(self.state.stack):
            print(' '*4, s)
