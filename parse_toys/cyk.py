from typing import Dict, Optional, Tuple, Union, Sequence

from parse_toys.grammar import Symbol, Epsilon, Grammar
from parse_toys.chomsky_normal_form import to_chomsky_normal_form

__all__ = ['parse_with_cyk']


def parse_with_cyk(grammar: Grammar, sentence: str):
    grammar.init_nullable()
    cnf_grammar, head_mapping = to_chomsky_normal_form(
        grammar,
        return_mapping=True,
        remove_unreachable=False)
    n = len(sentence)
    # Create the recognition table
    rec = [[set() for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for head, productions in cnf_grammar.productions.items():
            for production in productions:
                if len(production) == 1 and production[0].symbol == sentence[i]:
                    rec[i][i].add(head)
                    break
    for sub_len in range(1, n):
        for i in range(n - sub_len):
            j = i + sub_len
            for head, productions in cnf_grammar.productions.items():
                for production in productions:
                    if len(production) == 2:
                        for k in range(i, j):
                            if production[0] in rec[i][k] and production[1] in rec[k + 1][j]:
                                rec[i][j].add(head)
                                break
                    if head in rec[i][j]:
                        break
    # Undoing the effect of CNF transformation
    history: Dict[Tuple, Optional[Union[Tuple, str]]] = {}

    def _recognisable(symbol: Symbol, start: int, stop: int):
        if start > stop:
            return symbol.nullable is True
        if grammar.is_terminal(symbol):
            return symbol.symbol == sentence[start:stop + 1]
        if symbol in head_mapping:
            symbol = head_mapping[symbol]
        return symbol in rec[start][stop]

    def _parse_production(production: Sequence[Symbol], start: int, stop: int):
        if len(production) == 0:
            if start > stop:
                return ()
            return None
        first, rest = production[0], production[1:]
        if grammar.is_terminal(first):
            first_result = _parse_symbol(first, start, min(start, stop))
            if first_result is not None:
                rest_result = _parse_production(rest, start + 1, stop)
                if rest_result is not None:
                    return (first_result,) + rest_result
        else:
            for k in range(start - 1, stop + 1):
                first_result = _parse_symbol(first, start, k)
                if first_result is not None:
                    rest_result = _parse_production(rest, k + 1, stop)
                    if rest_result is not None:
                        return (first_result,) + rest_result
        return None

    def _parse_symbol(symbol: Symbol, start: int, stop: int):
        # This is similar to Unger parsing
        key = (symbol, start, stop)
        if key in history:
            return history[key]
        history[key] = None
        if grammar.is_terminal(symbol):
            if _recognisable(symbol, start, stop):
                history[key] = str(symbol)
        else:
            if _recognisable(symbol, start, stop):
                for production in grammar.productions[symbol]:
                    result = _parse_production(production, start, stop)
                    if result is not None:
                        if len(production) == 1 and grammar.is_terminal(production[0]):
                            history[key] = result
                        else:
                            history[key] = (f'{" ".join(map(str, production))}', result)
                        break
        return history[key]

    return _parse_symbol(grammar.start, 0, len(sentence) - 1)
