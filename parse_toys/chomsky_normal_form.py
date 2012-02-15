import copy
from typing import Dict

from parse_toys.grammar import Symbol, Productions, Grammar

__all__ = ['eliminate_epsilon_rules']


def eliminate_epsilon_rules(grammar: Grammar, init_nullable: bool = True):
    grammar = grammar.clone()
    if init_nullable:
        grammar.init_nullable()
    head_mapping: Dict[Symbol, Symbol] = {}
    # Create new productions without epsilon
    heads = list(grammar.productions.keys())
    for head in heads:
        productions = grammar.productions[head]
        if any([any(map(lambda x: x.nullable, production)) for production in productions]):
            new_head = grammar.create_aux(head)
            new_head.nullable = False
            for production in productions:
                if any([symbol.nullable for symbol in production]):
                    new_productions = [[]]
                    for symbol in production:
                        if symbol.nullable:
                            dup_productions = [copy.copy(prod) for prod in new_productions]
                            for prod in dup_productions:
                                prod.append(symbol)
                            new_productions.extend(dup_productions)
                        else:
                            for prod in new_productions:
                                prod.append(symbol)
                    for new_production in new_productions:
                        if len(new_production) == 0:
                            continue
                        if len(new_production) == 1 and new_production[0] == grammar.empty_symbol:
                            continue
                        grammar.add_production(new_head, new_production)
                else:
                    grammar.add_production(new_head, production)
            head_mapping[head] = new_head
    # Replace symbols with new ones
    heads = set(grammar.productions.keys())
    for head in heads:
        productions = grammar.productions[head]
        if head in head_mapping:
            grammar.remove(head)
            continue
        new_productions = []
        for index, production in enumerate(productions):
            if any([symbol in heads
                    and head_mapping.get(symbol, symbol) not in grammar.productions
                    for symbol in production]):
                continue
            new_productions.append((head_mapping.get(symbol, symbol) for symbol in production))
        if len(new_productions) == 0:
            grammar.remove(head)
            continue
        grammar.productions[head] = Productions(new_productions)
    # Replace start symbol
    if grammar.start in head_mapping:
        old_start = grammar.start
        grammar.start = head_mapping[grammar.start]
        if old_start.nullable:
            grammar.add_production(grammar.start, [grammar.empty_symbol])
            grammar.start.nullable = True
    return grammar
