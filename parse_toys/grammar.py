from typing import Optional, Sequence, Dict, Union, Set
from collections import OrderedDict, deque

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

    def __repr__(self):
        return '`' + self.symbol + '`'

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

    def add(self, production: Sequence[Symbol]):
        production = tuple(production)
        if not self.exist(production):
            self.productions.append(tuple(production))

    def exist(self, production: Sequence[Symbol]):
        production = tuple(production)
        if production in self:
            return True
        return False


class Grammar(object):

    def __init__(self):
        self.start = None
        self.symbols: Dict[str, Symbol] = {}
        self.composes: Dict[Symbol, Set[Symbol]] = {}
        self.productions: Dict[Symbol, Productions] = OrderedDict()
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

    def reset(self):
        self.start = None
        self.symbols = {}
        self.composes = {}
        self.productions = OrderedDict()

    def get_or_create_symbol(self, symbol: str):
        if symbol not in self.symbols:
            self.symbols[symbol] = Symbol(symbol)
        return self.symbols[symbol]

    def add_production(self, head: Symbol, production: Sequence[Symbol]):
        for symbol in production:
            if symbol not in self.composes:
                self.composes[symbol] = set()
            self.composes[symbol].add(head)
        if head in self.productions:
            self.productions[head].add(production)
        else:
            self.productions[head] = Productions([production])

    def parse(self, text: str):
        self.reset()
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
            head = self.get_or_create_symbol(tokens[start])
            if self.start is None:
                self.start = head
            start += 2
            production = []
            for j in range(start, stop):
                if tokens[j] == '|':
                    if len(production) == 0:
                        raise RuntimeError(f'Production should not be empty for symbol: {head}')
                    self.add_production(head, production)
                    production = []
                elif tokens[j] in {'ε', 'ϵ'}:
                    production.append(self.empty_symbol)
                else:
                    production.append(self.get_or_create_symbol(tokens[j]))
            if len(production) == 0:
                raise RuntimeError(f'Production should not be empty for symbol: {head}')
            self.add_production(head, production)

    def is_terminal(self, symbol: Union[str, Symbol]):
        if isinstance(symbol, str):
            symbol = Symbol(symbol)
        return symbol not in self.productions

    def is_non_terminal(self, symbol: Union[str, Symbol]):
        if isinstance(symbol, str):
            symbol = Symbol(symbol)
        return symbol in self.productions

    def init_nullable(self):
        queue, in_queue = deque(), set()
        for symbol in self.symbols.values():
            queue.append(symbol)
            in_queue.add(symbol)
        while len(queue) > 0:
            symbol = queue.popleft()
            in_queue.remove(symbol)
            if self.is_terminal(symbol):
                symbol.nullable = isinstance(symbol, Epsilon)
            else:
                for production in self.productions[symbol]:
                    if all([child.nullable is True for child in production]):
                        symbol.nullable = True
                        for head in self.composes.get(symbol, ()):
                            if head.nullable is not True and head not in in_queue:
                                queue.append(head)
                                in_queue.add(head)
                        break
                else:
                    symbol.nullable = False

    def init_min_length(self):
        attr_name = 'min_length'
        queue, in_queue = deque(), set()
        setattr(self.empty_symbol, attr_name, 0)
        for symbol in self.symbols.values():
            if self.is_terminal(symbol):
                setattr(symbol, attr_name, len(str(symbol)))
            else:
                queue.append(symbol)
                in_queue.add(symbol)
                setattr(symbol, attr_name, 1e100)
        while len(queue) > 0:
            symbol = queue.popleft()
            in_queue.remove(symbol)
            min_length = getattr(symbol, attr_name)
            for production in self.productions[symbol]:
                min_length = min(min_length, sum([getattr(child, attr_name) for child in production]))
            if min_length < getattr(symbol, attr_name):
                setattr(symbol, attr_name, min_length)
                for head in self.composes.get(symbol, ()):
                    if head not in in_queue:
                        queue.append(head)
                        in_queue.add(head)
