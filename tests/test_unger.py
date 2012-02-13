from unittest import TestCase

from parse_toys import Grammar, parse_with_unger


class TestUnger(TestCase):

    def test_case_1(self):
        grammar = Grammar()
        grammar.parse("""
            Expr -> Expr + Term | Term
            Term -> Term × Factor | Factor
            Factor -> ( Expr ) | i
        """)
        result = parse_with_unger(grammar, '(i+i)×i')
        self.assertEqual(result,
                         ('Term',
                          ('Term × Factor',
                           ('Factor',
                            ('( Expr )',
                             '(',
                             ('Expr + Term',
                              ('Term',
                               ('Factor',
                                ('i', 'i'))),
                              '+',
                              ('Factor',
                               ('i', 'i'))),
                             ')')),
                           '×',
                           ('i', 'i'))))

    def test_case_2(self):
        grammar = Grammar()
        grammar.parse("""
            S -> L S D | ε
            L -> ε
            D -> d
        """)
        result = parse_with_unger(grammar, 'd')
        self.assertEqual(result, ('L S D', ('ε', 'ε'), ('ε', 'ε'), ('d', 'd')))

    def test_case_3(self):
        grammar = Grammar()
        grammar.parse("""
            S -> L S D | ε
            L -> ε
            D -> d
        """)
        result = parse_with_unger(grammar, 'dd')
        self.assertEqual(result, ('L S D',
                                  ('ε', 'ε'),
                                  ('L S D',
                                   ('ε', 'ε'),
                                   ('ε', 'ε'),
                                   ('d', 'd')),
                                  ('d', 'd')))
