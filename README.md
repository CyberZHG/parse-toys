# Parsing Toys

[![Build Status](https://www.travis-ci.com/CyberZHG/parse-toys.svg?branch=master)](https://www.travis-ci.com/CyberZHG/parse-toys)
[![Coverage](https://coveralls.io/repos/github/CyberZHG/parse-toys/badge.svg?branch=master)](https://coveralls.io/github/CyberZHG/parse-toys)

## Install

```bash
pip install git+https://github.com/cyberzhg/parse-toys
```

## Methods

### General Non-Directional Parsing

#### Unger Parsing

```python
from parse_toys import Grammar, parse_with_unger

grammar = Grammar()
grammar.parse("""
    Expr -> Expr + Term | Term
    Term -> Term × Factor | Factor
    Factor -> ( Expr ) | i
""")
parsed = parse_with_unger(grammar, '(i+i)×i')
print(parsed)
"""
('Term',
    ('Term × Factor',
        ('Factor', 
            ('( Expr )',
                '(',
                ('Expr + Term', ('Term', ('Factor', ('i', 'i'))),
                '+',
                ('Factor', ('i', 'i'))),')')),
        '×',
        ('i', 'i'))))
"""
```

#### Chomsky Normal Form

```python
from parse_toys import Grammar, to_chomsky_normal_form

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
print(grammar)
"""
  Number -> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
          | Integer Digit
          | Integer Fraction
          | N_1 Scale_1
 Integer -> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
          | Integer Digit
Fraction -> T_1 Integer
   Digit -> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
    Sign -> + | -
 Scale_1 -> N_2 Integer
     N_1 -> Integer Fraction
     T_1 -> .
     T_2 -> e
     N_2 -> T_2 Sign
"""
```

#### CYK Parsing

```python
from parse_toys import Grammar, parse_with_cyk

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

parsed = parse_with_cyk(grammar, '32.5')
print(parsed)
"""
('Real',
    (('Integer Fraction Scale',
        (('Integer Digit', (('Digit', (('3',),)), ('2',))),
        ('. Integer', ('.', ('Digit', (('5',),)))),
        ('Empty', (('ε',),)))),)))
"""

parsed = parse_with_cyk(grammar, '32.5e+1')
print(parsed)
"""
('Real',
    (('Integer Fraction Scale',
        (('Integer Digit', (('Digit', (('3',),)), ('2',))),
        ('. Integer', ('.', ('Digit', (('5',),)))),
        ('e Sign Integer', ('e', ('+',), ('Digit', (('1',),)))))),))
"""
```
