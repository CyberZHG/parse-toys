from unittest import TestCase

from parse_toys import Symbol, Productions, Grammar


class TestGrammar(TestCase):

    def test_has_production(self):
        prod = Productions([
            [Symbol('A'), Symbol('B'), Symbol('C')],
            [Symbol('D'), Symbol('E')],
            [Symbol('F')],
        ])
        self.assertTrue(prod.has_production((Symbol('D'), Symbol('E'))))
        self.assertTrue(prod.has_production([Symbol('D'), Symbol('E')]))
        self.assertFalse(prod.has_production((Symbol('D'),)))
        self.assertFalse(prod.has_production((Symbol('D'), Symbol('E'), Symbol('F'))))
        self.assertEqual(str(prod), 'A B C | D E | F')

    def test_parse_case_1(self):
        grammar = Grammar()
        grammar.parse('S -> A B C | D E | F')
        grammar = str(grammar)
        self.assertEqual(grammar, """
S -> A B C
   | D E
   | F
"""[1:])

    def test_parse_case_2(self):
        grammar = Grammar()
        grammar.parse("""  S -> A B C
        | D E |
        F
        """)
        grammar = str(grammar)
        self.assertEqual(grammar, """
S -> A B C
   | D E
   | F
"""[1:])

    def test_parse_case_3(self):
        grammar = Grammar()
        grammar.parse("""
S -> A B C
S -> D E
S -> F
        """)
        grammar = str(grammar)
        self.assertEqual(grammar, """
S -> A B C
   | D E
   | F
"""[1:])

    def test_parse_case_4(self):
        grammar = Grammar()
        grammar.parse("""
Number -> Integer | Real
Integer -> Digit | Integer Digit
Real -> Integer Fraction Scale
Fraction -> . Integer
Scale -> e Sign Integer | Empty
Digit -> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
Sign -> + | -
Empty -> ε
        """)
        self.assertTrue(grammar.is_terminal('e'))
        self.assertTrue(grammar.is_terminal('ε'))
        self.assertTrue(grammar.is_non_terminal('Sign'))
        grammar.init_nullable()
        grammar = str(grammar)
        self.assertEqual(grammar, """
  Number -> Integer
          | Real
 Integer -> Digit
          | Integer Digit
    Real -> Integer Fraction Scale
Fraction -> . Integer
   Scale -> e Sign Integer
          | Empty
   Digit -> 0
          | 1
          | 2
          | 3
          | 4
          | 5
          | 6
          | 7
          | 8
          | 9
    Sign -> +
          | -
   Empty -> ε
"""[1:])

    def test_parse_error_case_head(self):
        grammar = Grammar()
        with self.assertRaises(RuntimeError):
            grammar.parse('S S -> A B C | D E | F')

    def test_parse_error_case_empty_mid(self):
        grammar = Grammar()
        with self.assertRaises(RuntimeError):
            grammar.parse('S -> A B C | | F')

    def test_parse_error_case_empty_all(self):
        grammar = Grammar()
        with self.assertRaises(RuntimeError):
            grammar.parse('S ->')
