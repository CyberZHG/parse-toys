from typing import Optional, Sequence, Dict, Set
from collections import OrderedDict

__all__ = ['Symbol', 'Epsilon', 'Productions', 'Grammar']


class Symbol(object):

    def __init__(self,
                 symbol: str,
                 terminal: Optional[bool] = None,
                 auxiliary: bool = False,
                 nullable: Optional[bool] = None):
        """Initialize a symbol.

        :param symbol: The name of the symbol.
        :param terminal: Whether it is a terminal.
        :param auxiliary: Whether it is created for parsing.
        :param nullable: Whether the symbol can produce null.
        """
        self.symbol = symbol
        self.terminal = terminal
        self.auxiliary = auxiliary
        self.nullable = nullable

    def __str__(self):
        return self.symbol

    def __hash__(self):
        return hash(self.symbol)

    def __eq__(self, other):
        return self.symbol == other.symbol


class Epsilon(Symbol):

    def __init__(self):
        super().__init__(symbol='ε', terminal=True, auxiliary=False, nullable=True)


class ProductionIterator(object):

    def __init__(self, production: 'Production'):
        self.index = 0
        self.production = production

    def __next__(self):
        if self.index >= len(self.production.productions):
            raise StopIteration
        production = self.production.productions[self.index]
        self.index += 1
        return production


class Productions(object):

    def __init__(self,
                 productions: Sequence[Sequence[Symbol]]):
        self.productions = [tuple(production) for production in productions]

    def __iter__(self):
        return ProductionIterator(self)

    def __len__(self):
        return len(self.productions)

    def __getitem__(self, index):
        return self.productions[index]

    def __str__(self):
        return ' | '.join(map(lambda x: ' '.join(map(str, x)), self.productions))

    def has_production(self, production: Sequence[Symbol]):
        production = tuple(production)
        if production in self:
            return True
        return False


class Grammar(object):

    def __init__(self):
        self.productions: Dict[Symbol, Productions] = OrderedDict()
        self.terminals: Set[Symbol] = set()
        self.non_terminals: Set[Symbol] = set()
        self.empty_symbol = Epsilon()

    def __str__(self):
        longest = max(len(str(symbol)) for symbol in self.productions.keys())
        text = ''
        for symbol, productions in self.productions.items():
            symbol = str(symbol)
            text += ' ' * (longest - len(symbol)) + symbol + ' -> ' + ' '.join(map(str, productions[0])) + '\n'
            for i in range(1, len(productions)):
                text += ' ' * (longest + len(' -')) + '| ' + ' '.join(map(str, productions[i])) + '\n'
        return text

    def parse(self, text: str):
        tokens = [token for token in text.replace('\n', ' ').replace('\r', ' ').split(' ') if len(token) > 0]
        split_indices = []
        for i, token in enumerate(tokens):
            if token == '->':
                split_indices.append(i - 1)
        split_indices.append(len(tokens))
        if split_indices[0] != 0:
            raise RuntimeError(f'Head should only contain one symbol, but found: '
                               f'{" ".join(tokens[:split_indices[0] + 1])}')
        for i in range(len(split_indices) - 1):
            start, stop = split_indices[i], split_indices[i + 1]
            head = Symbol(tokens[start])
            start += 2
            productions, production = [], []
            for j in range(start, stop):
                if tokens[j] == '|':
                    if len(production) == 0:
                        raise RuntimeError(f'Production should not be empty for symbol: {head}')
                    productions.append(production)
                    production = []
                elif tokens[j] in {'ε', 'ϵ'}:
                    production.append(self.empty_symbol)
                else:
                    production.append(Symbol(tokens[j]))
            if len(production) == 0:
                raise RuntimeError(f'Production should not be empty for symbol: {head}')
            productions.append(production)
            if head in self.productions:
                self.productions[head].productions.extend(productions)
            else:
                self.productions[head] = Productions(productions)
