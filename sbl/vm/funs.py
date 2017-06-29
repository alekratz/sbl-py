from sbl.common import *
from . val import *


def plus_op(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    if lhs.type != rhs.type:
        raise VMError(f"{lhs.type} is not compatible with {rhs.type}", vm_state.vm, *vm_state.current_loc())
    # TODO : string concatenation
    #if {lhs.type, rhs.type} == {ValType.CHAR, ValType.STRING}:
    vm_state.push(Val(lhs.val + rhs.val, lhs.type))


def times_op(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    if lhs.type is not rhs.type:
        raise VMError(f"{lhs.type} is not compatible with {rhs.type}", vm_state.vm, *vm_state.current_loc())
    vm_state.push(Val(lhs.val * rhs.val, lhs.type))


def minus_op(vm_state):
    rhs = vm_state.pop()
    lhs = vm_state.pop()
    if lhs.type is not rhs.type:
        raise VMError(f"{lhs.type} is not compatible with {rhs.type}", vm_state.vm, *vm_state.current_loc())
    vm_state.push(Val(lhs.val - rhs.val, lhs.type))


def div_op(vm_state):
    rhs = vm_state.pop()
    lhs = vm_state.pop()
    if lhs.type is not rhs.type:
        raise VMError(f"{lhs.type} is not compatible with {rhs.type}", vm_state.vm, *vm_state.current_loc())
    if rhs.type is ValType.INT and rhs == 0:
        raise VMError("attempted to divide by zero", vm_state.vm, *vm_state.current_loc())
    vm_state.push(Val(lhs.val / rhs.val, lhs.type))


def equals_op(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    vm_state.push(Val(lhs == rhs, ValType.BOOL))


def nequals_op(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    vm_state.push(Val(lhs != rhs, ValType.BOOL))


def ltequals_op(vm_state):
    rhs = vm_state.pop()
    lhs = vm_state.pop()
    vm_state.push(Val(lhs <= rhs, ValType.BOOL))


def gtequals_op(vm_state):
    rhs = vm_state.pop()
    lhs = vm_state.pop()
    vm_state.push(Val(lhs >= rhs, ValType.BOOL))


def less_than_op(vm_state):
    rhs = vm_state.pop()
    lhs = vm_state.pop()
    vm_state.push(Val(lhs < rhs, ValType.BOOL))


def greater_than_op(vm_state):
    rhs = vm_state.pop()
    lhs = vm_state.pop()
    vm_state.push(Val(lhs > rhs, ValType.BOOL))


def print_fn(vm_state):
    item = vm_state.pop()
    if item.type == ValType.NIL:
        print('Nil', end='')
    else:
        print(str(item), end='')


def println_fn(vm_state):
    print_fn(vm_state)
    print()


def stack_size_fn(vm_state):
    vm_state.push(Val(len(vm_state.stack), ValType.INT))


def tos_fn(vm_state):
    vm_state.push(vm_state.stack[-1])


def pop_fn(vm_state):
    tos = vm_state.pop()
    if tos.type is not ValType.STACK:
        raise VMError(f"expected a stack for `pop` function; instead got {tos.type}", vm_state.vm,
                      *vm_state.current_loc())
    val = tos.val.pop()
    vm_state.push(tos)
    vm_state.push(val)


def len_fn(vm_state):
    tos = vm_state.pop()
    if tos.type not in [ValType.STACK, ValType.STRING]:
        raise VMError(f"expected a stack or string for `len` function; instead got {tos.type}", vm_state.vm,
                      *vm_state.current_loc())
    vm_state.push(Val(len(tos.val), ValType.INT))


def open_fn(vm_state):
    mode_val = vm_state.pop()
    if mode_val.type != ValType.STRING:
        raise VMError(f'expected a string for the file mode; instead got {mode_val.type}', vm_state.vm,
                      *vm_state.current_loc())
    raise NotImplementedError()


BUILTINS = {
    # Arithmetic functions
    '+': plus_op,
    '*': times_op,
    '-': minus_op,
    '/': div_op,
    # Comparison functions
    '==': equals_op,
    '!=': nequals_op,
    '<=': ltequals_op,
    '>=': gtequals_op,
    '<': less_than_op,
    '>': greater_than_op,
    # Collection functions
    'pop': pop_fn,
    'len': len_fn,
    # Global stack functions
    '$': stack_size_fn,
    '^': tos_fn,
    # IO functions
    'open': open_fn,
    'print': print_fn,
    'println': println_fn,
}
