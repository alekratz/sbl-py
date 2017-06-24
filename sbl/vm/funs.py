from sbl.common import *
from . val import *


def plus(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    if lhs.type is not rhs.type:
        raise VMError(f"{lhs.type} is not compatible with {rhs.type}", vm_state.call_stack)
    #if {lhs.type, rhs.type} == {ValType.CHAR, ValType.STRING}:
    vm_state.push(Val(lhs.val + rhs.val, lhs.type))


def times(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    if lhs.type is not rhs.type:
        raise VMError(f"{lhs.type} is not compatible with {rhs.type}", vm_state.call_stack)
    vm_state.push(Val(lhs.val * rhs.val, lhs.type))


def minus(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    if lhs.type is not rhs.type:
        raise VMError(f"{lhs.type} is not compatible with {rhs.type}", vm_state.call_stack)
    vm_state.push(Val(lhs.val - rhs.val, lhs.type))


def div(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    if lhs.type is not rhs.type:
        raise VMError(f"{lhs.type} is not compatible with {rhs.type}", vm_state.call_stack)
    if rhs.type is ValType.INT and rhs == 0:
        raise VMError("attempted to divide by zero", vm_state.call_stack)
    vm_state.push(Val(lhs.val / rhs.val, lhs.type))


def print_fn(vm_state):
    item = vm_state.pop()
    print(item, end='')


BUILTINS = {
    '+': plus,
    '*': times,
    '-': minus,
    '/': div,
    'print': print_fn,
}
