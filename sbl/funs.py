from common import *


def plus(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    vm_state.push(lhs + rhs)


def times(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    vm_state.push(lhs * rhs)


def minus(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    vm_state.push(lhs - rhs)


def div(vm_state):
    lhs = vm_state.pop()
    rhs = vm_state.pop()
    if rhs == 0:
        raise VMError("attempted to divide by zero", vm_state.call_stack)
    vm_state.push(int(lhs / rhs))


def print_fn(vm_state):
    item = vm_state.pop()
    print(item)


BUILTINS = {
    '+': plus,
    '*': times,
    '-': minus,
    '/': div,
    'print': print_fn,
}
