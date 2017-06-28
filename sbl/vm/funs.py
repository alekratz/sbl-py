from sbl.common import *
from . val import *


def plus(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    if lhs.type != rhs.type:
        raise VMError(f"{lhs.type} is not compatible with {rhs.type}", vm_state.vm, *vm_state.current_loc())
    # TODO : string concatenation
    #if {lhs.type, rhs.type} == {ValType.CHAR, ValType.STRING}:
    vm_state.push(Val(lhs.val + rhs.val, lhs.type))


def times(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    if lhs.type is not rhs.type:
        raise VMError(f"{lhs.type} is not compatible with {rhs.type}", vm_state.vm, *vm_state.current_loc())
    vm_state.push(Val(lhs.val * rhs.val, lhs.type))


def minus(vm_state):
    rhs = vm_state.pop()
    lhs = vm_state.pop()
    if lhs.type is not rhs.type:
        raise VMError(f"{lhs.type} is not compatible with {rhs.type}", vm_state.vm, *vm_state.current_loc())
    vm_state.push(Val(lhs.val - rhs.val, lhs.type))


def div(vm_state):
    rhs = vm_state.pop()
    lhs = vm_state.pop()
    if lhs.type is not rhs.type:
        raise VMError(f"{lhs.type} is not compatible with {rhs.type}", vm_state.vm, *vm_state.current_loc())
    if rhs.type is ValType.INT and rhs == 0:
        raise VMError("attempted to divide by zero", vm_state.vm, *vm_state.current_loc())
    vm_state.push(Val(lhs.val / rhs.val, lhs.type))


def equals(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    vm_state.push(Val(lhs == rhs, ValType.BOOL))


def print_fn(vm_state):
    item = vm_state.pop()
    if item.type == ValType.NIL:
        print('Nil', end='')
    else:
        print(str(item), end='')


def println_fn(vm_state):
    item = vm_state.pop()
    if item.type == ValType.NIL:
        print('Nil')
    else:
        print(f"{str(item.val)}")


def stack_size_fn(vm_state):
    vm_state.push(Val(len(vm_state.stack), ValType.INT))


def tos_fn(vm_state):
    vm_state.push(vm_state.stack[-1])


def open_fn(vm_state):
    mode_val = vm_state.pop()
    if mode_val.type != ValType.STRING:
        raise VMError(f'expected a string for the file mode; instead got {mode_val.type}', vm_state.vm,
                      *vm_state.current_loc())
    raise NotImplementedError()


BUILTINS = {
    '+': plus,
    '*': times,
    '-': minus,
    '/': div,
    '==': equals,
    'print': print_fn,
    'println': println_fn,
    '$': stack_size_fn,
    '^': tos_fn,
    # IO functions
    'open': open_fn,
}

