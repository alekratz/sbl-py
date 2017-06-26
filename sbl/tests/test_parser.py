from unittest import TestCase
from sbl.syntax.parse import *


class TestParser(TestCase):
    def assert_item(self, item, type: ItemType, val):
        self.assertEqual(item.type, type)
        self.assertEqual(item.val, val)

    def assert_action(self, action: Action, items: List[Item], pop):
        self.assertEqual(len(action.items), len(items))
        self.assertEqual(action.pop, pop)
        for lhs, rhs in zip(action.items, items):
            self.assertEqual(lhs.type, rhs.type)
            self.assertEqual(lhs.val, rhs.val)

    def assert_branch(self, branch: Branch, br_block: List[Line], el_block: Optional[List[Line]]=None):
        self.assert_block(branch.br_block.lines, br_block)
        self.assert_block(branch.el_block.lines, el_block)

    def assert_loop(self, loop: Loop, block: List[Line]):
        self.assert_block(loop.block, block)

    def assert_block(self, lhs: List[Line], rhs: List[Line]):
        self.assertEqual(lhs is None, rhs is None)
        if lhs is None: return
        self.assertEqual(len(lhs), len(rhs))
        for a, b in zip(lhs, rhs):
            self.assertIsInstance(b, type(a))
            self.assertIn(type(a), [Action, Branch, Loop])
            if type(a) is Action:
                self.assert_action(a, b.items, a.pop)
            elif type(a) is Branch:
                self.assert_branch(a, b.br_block, b.el_block)
            elif type(a) is Loop:
                self.assert_loop(a, b.block)

    def assert_fun(self, fun: FunDef, name: str, lines: List[Line]):
        self.assertEqual(fun.name, name)
        self.assert_block(fun.block.lines, lines)

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
            Action(None, [
                Item(None, 'foo', ItemType.IDENT),
                Item(None, 'bar', ItemType.IDENT),
                Item(None, 'baz', ItemType.IDENT),
            ], False)
        ])
        self.assert_branch(p._expect_branch(), [
                Action(None, [
                    Item(None, 'a', ItemType.IDENT),
                    Item(None, 'b', ItemType.IDENT),
                    Item(None, 'c', ItemType.IDENT),
                ], True),
            ], [Action(None, [
                    Item(None, 0, ItemType.INT),
                    Item(None, 0, ItemType.INT),
                    Item(None, 0, ItemType.INT),
                ], False),
                Action(None, [
                    Item(None, 'a', ItemType.IDENT),
                    Item(None, 'b', ItemType.IDENT),
                    Item(None, 'c', ItemType.IDENT),
                ], True),
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
            Action(None, [Item(None, 'a', ItemType.IDENT),
                          Item(None, 'b', ItemType.IDENT),
                          Item(None, 'c', ItemType.IDENT)], True)
        ])
        self.assert_fun(p._expect_fundef(), 'main', [
            Action(None, [Item(None, 1, ItemType.INT),
                          Item(None, 2, ItemType.INT),
                          Item(None, 3, ItemType.INT)], False)
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
