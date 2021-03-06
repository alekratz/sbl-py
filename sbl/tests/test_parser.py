from unittest import TestCase

from sbl.syntax.parse import *


class TestParser(TestCase):
    def assert_item(self, item, type: ItemType, val):
        self.assertEqual((item.type, item.val), (type, val))

    def assert_action(self, action: StackStmt, items: List[Item], pop):
        self.assertEqual(len(action.items), len(items))
        for lhs, rhs in zip(action.items, items):
            self.assertEqual(lhs.item, rhs)

    def assert_branch(self, branch: Branch, br_block: List[Stmt], el_block: Optional[List[Stmt]]=None):
        self.assertEqual(branch.br_block.lines, br_block)
        self.assertEqual(branch.el_block.lines, el_block)

    def assert_loop(self, loop: Loop, block: List[Stmt]):
        self.assertEqual(loop.block, block)

    def assert_fun(self, fun: FunDef, name: str, lines: List[Stmt]):
        self.assertEqual(fun.name, name)
        self.assertEqual(fun.block.lines, lines)

    def test_items(self):
        p = Parser("""
                   123456789
                   0xabcdef12345
                   0b10101010101
                   foo bar baz
                   'f 'o 'o '\\0
                   "this is a test string"
                   """, 'test')
        self.assert_item(p._expect_item(), ItemType.INT, 123456789)
        self.assert_item(p._expect_item(), ItemType.INT, 0xabcdef12345)
        self.assert_item(p._expect_item(), ItemType.INT, 0b10101010101)
        self.assert_item(p._expect_item(), ItemType.IDENT, 'foo')
        self.assert_item(p._expect_item(), ItemType.IDENT, 'bar')
        self.assert_item(p._expect_item(), ItemType.IDENT, 'baz')
        self.assert_item(p._expect_item(), ItemType.CHAR, 'f')
        self.assert_item(p._expect_item(), ItemType.CHAR, 'o')
        self.assert_item(p._expect_item(), ItemType.CHAR, 'o')
        self.assert_item(p._expect_item(), ItemType.CHAR, '\0')
        self.assert_item(p._expect_item(), ItemType.STRING, 'this is a test string')
        self.assertTrue(p.is_end())

    def test_lines(self):
        p = Parser("""
                   . x y z;
                   1 a 2 b 3 c;
                   loop { foo bar baz; }
                   br {
                       . a b c;
                   }
                   el {
                       0 0 0;
                       . a b c;
                   }
                   """, 'test')

        self.assert_action(p._expect_action(), [
            Item(None, 'x', ItemType.IDENT),
            Item(None, 'y', ItemType.IDENT),
            Item(None, 'z', ItemType.IDENT)], True)
        self.assert_action(p._expect_action(), [
            Item(None, 1, ItemType.INT),
            Item(None, 'a', ItemType.IDENT),
            Item(None, 2, ItemType.INT),
            Item(None, 'b', ItemType.IDENT),
            Item(None, 3, ItemType.INT),
            Item(None, 'c', ItemType.IDENT)], False)
        self.assert_loop(p._expect_loop(), [
            StackStmt(None, [
                StackAction(None, Item(None, 'foo', ItemType.IDENT), False),
                StackAction(None, Item(None, 'bar', ItemType.IDENT), False),
                StackAction(None, Item(None, 'baz', ItemType.IDENT), False),
            ])
        ])
        self.assert_branch(p._expect_branch(), [
                StackStmt(None, [
                    StackAction(None, Item(None, 'a', ItemType.IDENT), True),
                    StackAction(None, Item(None, 'b', ItemType.IDENT), False),
                    StackAction(None, Item(None, 'c', ItemType.IDENT), False),
                ]),
            ], [StackStmt(None, [
                    StackAction(None, Item(None, 0, ItemType.INT), False),
                    StackAction(None, Item(None, 0, ItemType.INT), False),
                    StackAction(None, Item(None, 0, ItemType.INT), False),
                ]),
                StackStmt(None, [
                    StackAction(None, Item(None, 'a', ItemType.IDENT), True),
                    StackAction(None, Item(None, 'b', ItemType.IDENT), False),
                    StackAction(None, Item(None, 'c', ItemType.IDENT), False),
                ]),
            ])
        self.assertTrue(p.is_end())

    def test_fundef(self):
        p = Parser("""
            foo { }
            bar { . a b c; }
            main { 1 2 3; }
            """, 'test')
        self.assert_fun(p._expect_fundef(), 'foo', [])
        self.assert_fun(p._expect_fundef(), 'bar', [
            StackStmt(None, [
                StackAction(None, Item(None, 'a', ItemType.IDENT), True),
                StackAction(None, Item(None, 'b', ItemType.IDENT), False),
                StackAction(None, Item(None, 'c', ItemType.IDENT), False),
            ])
        ])
        self.assert_fun(p._expect_fundef(), 'main', [
            StackStmt(None, [
                StackAction(None, Item(None, 1, ItemType.INT), False),
                StackAction(None, Item(None, 2, ItemType.INT), False),
                StackAction(None, Item(None, 3, ItemType.INT), False),
            ])
        ])
        self.assertTrue(p.is_end())

    def test_import(self):
        p = Parser("""
            import "basic.sbl";
            import "foo.sbl";
            import "bar.sbl";
            """, 'test')
        self.assertEqual(p._expect_import().path, 'basic.sbl')
        self.assertEqual(p._expect_import().path, 'foo.sbl')
        self.assertEqual(p._expect_import().path, 'bar.sbl')
        self.assertTrue(p.is_end())
