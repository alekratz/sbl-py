from sbl.syntax.parse import *
from sbl.vm.bc import *
from sbl.vm.funs import BUILTINS


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
        for stmt in block:
            if isinstance(stmt, StackStmt):
                bc += self._compile_stack_stmt(stmt)
            elif isinstance(stmt, Branch):
                start_addr = len(bc) # this is where we insert the first jump, later
                bc += [None]
                bc += self._compile_block(stmt.br_block, len(bc) + jmp_offset)
                if stmt.el_block:
                    end_addr = len(bc)
                    bc += [None]
                    bc[start_addr] = BC.jmpz(self._meta_with(where=stmt.br_block.range), Val(jmp_offset + end_addr + 1,
                                                                                             ValType.INT))
                    bc += self._compile_block(stmt.el_block, len(bc))
                    bc[end_addr] = BC.jmp(self._meta_with(where=stmt.el_block.range), Val(len(bc) + jmp_offset,
                                                                                          ValType.INT))
                else:
                    end_addr = len(bc) + jmp_offset
                    bc[start_addr] = BC.jmpz(self._meta_with(where=stmt.br_block.range), Val(end_addr, ValType.INT))
            elif isinstance(stmt, Loop):
                start_addr = len(bc)
                bc += [None]
                bc += self._compile_block(stmt.block, len(bc) + jmp_offset)
                bc += [BC.jmp(self._meta_with(where=stmt.block.range), Val(start_addr + jmp_offset, ValType.INT))]
                end_addr = len(bc) + jmp_offset
                bc[start_addr] = BC.jmpz(self._meta_with(where=stmt.block.range), Val(end_addr, ValType.INT))
            else:
                assert False, f"stmt was neither an action nor a branch: {stmt}"
        return bc

    def _compile_stack_stmt(self, stmt: StackStmt) -> List[BC]:
        bc = []
        for action in stmt.items:
            item = action.item
            if action.pop:
                meta = self._meta_with(where=item.range)
                assert item.type in [ItemType.IDENT, ItemType.NIL, ItemType.INT], \
                    f'item type for pop StackAction was not ident, nil, or int: {stmt.item.type}'
                bc += [BC.pop(meta, item.to_val())]
            else:
                bc += self._compile_item_push(item)
        return bc

    def _compile_item_push(self, item: Item) -> List[BC]:
        meta = self._meta_with(where=item.range)
        if item.val in self.fun_names + list(self.builtins.keys()):
            bc = [BC.call(meta, item.to_val())]
        elif item.type is ItemType.IDENT:
            bc = [BC.load(meta, item.to_val())]
        elif item.type is ItemType.STACK:
            bc = self._compile_local_stack(item)
        else:
            bc = [BC.push(meta, item.to_val())]
        return bc

    def _compile_local_stack(self, item: Item) -> List[BC]:
        assert item.type is ItemType.STACK, 'called _compile_local_stack with non-ItemType.STACK item'
        bc = []
        meta = self._meta_with(where=item.range)
        if item.is_const():
            # allow the stack to be a single value because nothing has to be loaded
            bc += [BC.push(meta, item.to_val())]
        else:
            assert isinstance(item.val, list)
            bc += [BC.push(meta, Val([], ValType.STACK))]
            for item_val in item.val:
                bc += self._compile_item_push(item_val) + [BC.pushl(meta)]
        return bc
