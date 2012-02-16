from unittest import TestCase

from parse_toys import Grammar, parse_with_cyk


class TestCYK(TestCase):

    def _get_grammar_1(self):
        grammar = Grammar()
        grammar.parse("""
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
        """)
        return grammar

    def test_case_1_1(self):
        grammar = self._get_grammar_1()
        results = parse_with_cyk(grammar, '32')
        self.assertEqual(results, ('Integer', (('Integer Digit', (('Digit', (('3',),)), ('2',))),)))

    def test_case_1_2(self):
        grammar = self._get_grammar_1()
        results = parse_with_cyk(grammar, '32.5e+1')
        self.assertEqual(results, ('Real',
                                   (('Integer Fraction Scale',
                                     (('Integer Digit', (('Digit', (('3',),)), ('2',))),
                                      ('. Integer', ('.', ('Digit', (('5',),)))),
                                      ('e Sign Integer', ('e', ('+',), ('Digit', (('1',),)))))),)))

    def test_case_1_3(self):
        grammar = self._get_grammar_1()
        results = parse_with_cyk(grammar, '32.5')
        self.assertEqual(results, ('Real',
                                   (('Integer Fraction Scale',
                                     (('Integer Digit', (('Digit', (('3',),)), ('2',))),
                                      ('. Integer', ('.', ('Digit', (('5',),)))),
                                      ('Empty', (('ε',),)))),)))
