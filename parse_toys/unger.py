from typing import Dict, Optional, Tuple, Union

from parse_toys.grammar import Symbol, Epsilon, Grammar

__all__ = ['parse_with_unger']


def parse_with_unger(grammar: Grammar, sentence: str):
    grammar.init_nullable()
    grammar.init_min_length()
    history: Dict[Tuple, Optional[Union[Tuple, str]]] = {}

    def _divide(start: int, stop: int, parts: int, index: int = 0):
        if index + 1 == parts:
            yield (stop - start,)
        else:
            for i in range(start, stop + 1):
                for rest in _divide(i, stop, parts, index + 1):
                    yield (i - start,) + rest

    def _parse_symbol(symbol: Symbol, start: int, stop: int):
        key = (symbol, start, stop)
        if key in history:
            return history[key]
        history[key] = None

        if isinstance(symbol, Epsilon):
            if start == stop:
                history[key] = str(symbol)
        elif grammar.is_terminal(symbol):
            if str(symbol) == sentence[start:stop]:
                history[key] = str(symbol)
        else:
            for production in grammar.productions[symbol]:
                for division in _divide(start, stop, len(production)):
                    valid = True
                    for i, div in enumerate(division):
                        if div == 0 and not production[i].nullable:
                            valid = False
                            break
                        if div < production[i].min_length:
                            valid = False
                            break
                    if not valid:
                        continue
                    results = []
                    sub_start, sub_stop = start, start
                    for i, div in enumerate(division):
                        sub_stop += div
                        result = _parse_symbol(production[i], sub_start, sub_stop)
                        if result is None:
                            valid = False
                            break
                        results.append(result)
                        sub_start = sub_stop
                    if valid:
                        history[key] = (f'{" ".join(map(str, production))}',) + tuple(results)
                        break
                if history[key] is not None:
                    break
        return history[key]

    return _parse_symbol(grammar.start, 0, len(sentence))
