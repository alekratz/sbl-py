from unittest import TestCase
from sbl.syntax.prepro import *
from sbl.vm.compile import *
from sbl.vm.bc import *
from sbl.vm.val import *


class TestCompiler(TestCase):
    def compile_source(self, source_text: str) -> FunTable:
        path = 'test'
        ast = Parser(source_text, path).parse()
        ast += Preprocess(path, [], ast).preprocess()
        return Compiler(ast, meta={'file': path}).compile()

    def test_push(self):
        fun_table = self.compile_source('''
            foo {
                a b c;
            }
            bar {
                1 2 3 4 5 6;
            }
        ''')
        self.assertIn('foo', fun_table)
        foo_fun = fun_table['foo']
        self.assertEqual(foo_fun.bc, [
            BC.load(None, Val('a', ValType.IDENT)),
            BC.load(None, Val('b', ValType.IDENT)),
            BC.load(None, Val('c', ValType.IDENT)),
            BC.ret(None),
        ])

        self.assertIn('bar', fun_table)
        bar_fun = fun_table['bar']
        self.assertEqual(bar_fun.bc, [
            BC.push(None, Val(1, ValType.INT)),
            BC.push(None, Val(2, ValType.INT)),
            BC.push(None, Val(3, ValType.INT)),
            BC.push(None, Val(4, ValType.INT)),
            BC.push(None, Val(5, ValType.INT)),
            BC.push(None, Val(6, ValType.INT)),
            BC.ret(None),
        ])

    def test_pop(self):
        fun_table = self.compile_source('''
            foo {
                .a .b .c;
                .@;
            }
        ''')
        self.assertIn('foo', fun_table)
        foo_fun = fun_table['foo']
        self.assertEqual(foo_fun.bc, [
            BC.pop(None, Val('a', ValType.IDENT)),
            BC.pop(None, Val('b', ValType.IDENT)),
            BC.pop(None, Val('c', ValType.IDENT)),
            BC.pop(None, Val(None, ValType.NIL)),
            BC.ret(None),
        ])
