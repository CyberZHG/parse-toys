from unittest import TestCase

from parse_toys import Grammar, eliminate_epsilon_rules


class TestChomskyNormalForm(TestCase):

    def test_eliminate_epsilon_rules_case_1(self):
        grammar = Grammar()
        grammar.parse("""
            S -> L a M
            L -> L M
            L -> ε
            M -> M M
            M -> ε
        """)
        grammar = eliminate_epsilon_rules(grammar)
        self.assertEqual(str(grammar), """
S_1 -> a
     | L_1 a
     | a M_1
     | L_1 a M_1
L_1 -> L_1
     | M_1
     | L_1 M_1
M_1 -> M_1
     | M_1 M_1
"""[1:])

    def test_eliminate_epsilon_rules_case_2(self):
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
        grammar = eliminate_epsilon_rules(grammar)
        self.assertEqual(str(grammar), """
  Number -> Integer
          | Real_1
 Integer -> Digit
          | Integer Digit
Fraction -> . Integer
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
  Real_1 -> Integer Fraction
          | Integer Fraction Scale_1
 Scale_1 -> e Sign Integer
"""[1:])

    def test_eliminate_epsilon_rules_case_3(self):
        grammar = Grammar()
        grammar.parse("""
            S -> L M
            L -> ε
            M -> ε
        """)
        grammar = eliminate_epsilon_rules(grammar)
        print(grammar)
        self.assertEqual(str(grammar), """
S_1 -> ε
"""[1:])
