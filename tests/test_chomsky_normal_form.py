from unittest import TestCase

from parse_toys import Grammar, eliminate_epsilon_rules, eliminate_unit_rules, to_chomsky_normal_form


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
        self.assertEqual(str(grammar), """
S_1 -> ε
"""[1:])

    def test_eliminate_epsilon_rules_case_4(self):
        grammar = Grammar()
        grammar.parse("""
            S -> L M | A
            A -> M L
            L -> ε
            M -> ε
        """)
        grammar = eliminate_epsilon_rules(grammar)
        self.assertEqual(str(grammar), """
S_1 -> ε
"""[1:])

    def test_eliminate_unit_rules_case_1(self):
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
        grammar = eliminate_unit_rules(grammar)
        self.assertEqual(str(grammar), """
  Number -> 0
          | 1
          | 2
          | 3
          | 4
          | 5
          | 6
          | 7
          | 8
          | 9
          | Integer Digit
          | Integer Fraction
          | Integer Fraction Scale_1
 Integer -> 0
          | 1
          | 2
          | 3
          | 4
          | 5
          | 6
          | 7
          | 8
          | 9
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

    def test_eliminate_unit_rules_case_2(self):
        grammar = Grammar()
        grammar.parse("""
            S -> A
            A -> B
            B -> C
            C -> D
            D -> E
            E -> F
            F -> a
        """)
        grammar = eliminate_epsilon_rules(grammar)
        grammar = eliminate_unit_rules(grammar)
        self.assertEqual(str(grammar), """
S -> a
A -> a
B -> a
C -> a
D -> a
E -> a
F -> a
"""[1:])

    def test_eliminate_unit_rules_case_3(self):
        grammar = Grammar()
        grammar.parse("""
            S -> A
            A -> A | a
        """)
        grammar = eliminate_epsilon_rules(grammar)
        grammar = eliminate_unit_rules(grammar)
        self.assertEqual(str(grammar), """
S -> A
   | a
A -> A
   | a
"""[1:])

    def test_chomsky_normal_form_case_1(self):
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
        grammar = to_chomsky_normal_form(grammar)
        self.assertEqual(str(grammar), """
  Number -> 0
          | 1
          | 2
          | 3
          | 4
          | 5
          | 6
          | 7
          | 8
          | 9
          | Integer Digit
          | Integer Fraction
          | N_1 Scale_1
 Integer -> 0
          | 1
          | 2
          | 3
          | 4
          | 5
          | 6
          | 7
          | 8
          | 9
          | Integer Digit
Fraction -> T_1 Integer
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
 Scale_1 -> N_2 Integer
     N_1 -> Integer Fraction
     T_1 -> .
     T_2 -> e
     N_2 -> T_2 Sign
"""[1:])

    def test_chomsky_normal_form_case_2(self):
        grammar = Grammar()
        grammar.parse("""
S -> A B C D
A -> B C D | a b c d
B -> C D | b c d
C -> C D | c d
D -> E H I | d
E -> F G
F -> F
G -> G
H -> B C D
I -> i
            """)
        grammar = to_chomsky_normal_form(grammar)
        self.assertEqual(str(grammar), """
  S -> N_2 D
  A -> N_3 D
     | N_5 T_4
  B -> C D
     | N_6 T_4
  C -> C D
     | T_3 T_4
  D -> N_7 I
     | d
  E -> F G
  F -> F
  G -> G
  H -> N_3 D
  I -> i
N_1 -> A B
N_2 -> N_1 C
N_3 -> B C
T_1 -> a
T_2 -> b
N_4 -> T_1 T_2
T_3 -> c
N_5 -> N_4 T_3
T_4 -> d
N_6 -> T_2 T_3
N_7 -> E H
"""[1:])
