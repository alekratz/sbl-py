from unittest import TestCase

from sbl.syntax.token import *


class TestTokens(TestCase):
    def check_token(self, token: Token, type: TokenType, payload: Any=None):
        self.assertEqual(token.type, type)
        self.assertEqual(token.payload, payload)

    def test_comments(self):
        t = Tokenizer("""
                      # comment
                      # comment
                      # comment again
                      # this is a comment
                      """, 'test')
        self.check_token(t.next(), TokenType.COMMENT)
        self.check_token(t.next(), TokenType.COMMENT)
        self.check_token(t.next(), TokenType.COMMENT)
        self.check_token(t.next(), TokenType.COMMENT)
        self.assertEqual(t.next(), None)
        self.assertTrue(t.is_end())

    def test_nums(self):
        t = Tokenizer("""
                      1234
                      0
                      123456
                      10000000000
                      0xabdef0123
                      0b010111001
                      """, 'test')
        def assert_num(token, payload): self.check_token(token, TokenType.NUM, payload)
        assert_num(t.next(), 1234)
        assert_num(t.next(), 0)
        assert_num(t.next(), 123456)
        assert_num(t.next(), 10000000000)
        assert_num(t.next(), 0xabdef0123)
        assert_num(t.next(), 0b010111001)
        self.assertEqual(t.next(), None)
        self.assertTrue(t.is_end())

    def test_strings(self):
        t = Tokenizer("""
                      "foo, bar, and baz"
                      "foo\\r\\n, bar\\", \\'and baz\\t"
                      "The Quick Brown Fox Jumped Over The Lazy Dogs\\0"
                      """, 'test')
        def assert_str(token, payload): self.check_token(token, TokenType.STRING, payload)
        assert_str(t.next(), "foo, bar, and baz")
        assert_str(t.next(), "foo\r\n, bar\", \'and baz\t")
        assert_str(t.next(), "The Quick Brown Fox Jumped Over The Lazy Dogs\0")
        self.assertEqual(t.next(), None)
        self.assertTrue(t.is_end())

    def test_chars(self):
        t = Tokenizer("""
                      'a 'b 'c
                      'd 'e 'f
                      '\\n '\\\\ '\\' '\\" '\\t '\\r '\\s '\\0
                      """, 'test')
        def assert_chr(token, payload): self.check_token(token, TokenType.CHAR, payload)
        assert_chr(t.next(), 'a')
        assert_chr(t.next(), 'b')
        assert_chr(t.next(), 'c')
        assert_chr(t.next(), 'd')
        assert_chr(t.next(), 'e')
        assert_chr(t.next(), 'f')
        assert_chr(t.next(), '\n')
        assert_chr(t.next(), '\\')
        assert_chr(t.next(), '\'')
        assert_chr(t.next(), '\"')
        assert_chr(t.next(), '\t')
        assert_chr(t.next(), '\r')
        assert_chr(t.next(), ' ')
        assert_chr(t.next(), '\0')
        self.assertEqual(t.next(), None)
        self.assertTrue(t.is_end())

    def test_idents(self):
        # well, idents and symbols
        t = Tokenizer("""
                      this-is-a-valid-ident
                      this!is!also!a!valid!ident
                      branch
                      else
                      looping
                      imported
                      br el loop import
                      
                      ! @ $ % ^ & * + - /
                      !! -- $$ @@ ** ++ //
                      . { } ;
                      """, 'test')
        def assert_ident(token, payload): self.check_token(token, TokenType.IDENT, payload)
        assert_ident(t.next(), 'this-is-a-valid-ident')
        assert_ident(t.next(), 'this!is!also!a!valid!ident')
        assert_ident(t.next(), 'branch')
        assert_ident(t.next(), 'else')
        assert_ident(t.next(), 'looping')
        assert_ident(t.next(), 'imported')
        self.check_token(t.next(), TokenType.BR)
        self.check_token(t.next(), TokenType.EL)
        self.check_token(t.next(), TokenType.LOOP)
        self.check_token(t.next(), TokenType.IMPORT)
        assert_ident(t.next(), '!')
        self.check_token(t.next(), TokenType.NIL)
        assert_ident(t.next(), '$')
        assert_ident(t.next(), '%')
        assert_ident(t.next(), '^')
        assert_ident(t.next(), '&')
        assert_ident(t.next(), '*')
        assert_ident(t.next(), '+')
        assert_ident(t.next(), '-')
        assert_ident(t.next(), '/')
        assert_ident(t.next(), '!!')
        assert_ident(t.next(), '--')
        assert_ident(t.next(), '$$')
        assert_ident(t.next(), '@@')
        assert_ident(t.next(), '**')
        assert_ident(t.next(), '++')
        assert_ident(t.next(), '//')
        self.check_token(t.next(), TokenType.DOT)
        self.check_token(t.next(), TokenType.LBRACE)
        self.check_token(t.next(), TokenType.RBRACE)
        self.check_token(t.next(), TokenType.SEMI)
        self.assertEqual(t.next(), None)
        self.assertTrue(t.is_end())
