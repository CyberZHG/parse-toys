import copy
from typing import Dict
from collections import deque

from parse_toys.grammar import Symbol, Grammar

__all__ = ['eliminate_epsilon_rules', 'eliminate_unit_rules']


def eliminate_epsilon_rules(grammar: Grammar, init_nullable: bool = True):
    """Eliminate ε-rules in the grammar.
    Only the start symbol can derive ε after the transformation.

    :param grammar: The old grammar.
    :param init_nullable: Can be False if the nullables were already calculated.
    :return: The new grammar.
    """
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
    heads = list(grammar.productions.keys())
    queue, in_queue = deque(), set()
    for head in heads:
        queue.append(head)
        in_queue.add(head)
    while len(queue) > 0:
        head = queue.popleft()
        in_queue.remove(head)
        productions = grammar.productions[head]
        grammar.remove(head)
        if head in head_mapping:
            continue
        for production in productions:
            if any([head_mapping.get(symbol, symbol) != head and symbol in heads
                    and head_mapping.get(symbol, symbol) not in grammar.productions
                    for symbol in production]):
                # The production will be left out if some of the symbols can only derive ε.
                continue
            grammar.add_production(head, [head_mapping.get(symbol, symbol) for symbol in production])
        if head not in grammar.productions:
            # This symbol can only derive ε.
            for symbol in grammar.composes.get(head, ()):
                if symbol not in head_mapping and symbol in grammar.productions and symbol not in in_queue:
                    queue.append(symbol)
                    in_queue.add(symbol)
            continue
    # Replace start symbol
    if grammar.start in head_mapping:
        old_start = grammar.start
        grammar.start = head_mapping[grammar.start]
        if old_start.nullable:
            grammar.add_production(grammar.start, [grammar.empty_symbol])
            grammar.start.nullable = True
    return grammar


def eliminate_unit_rules(grammar: Grammar):
    """Replace rules like A -> B and B -> α with A -> α.

    :param grammar: The old grammar.
    :return: The new grammar.
    """
    grammar = grammar.clone()
    queue, in_queue = deque(), set()
    for head in grammar.productions.keys():
        queue.append(head)
        in_queue.add(head)
    while len(queue) > 0:
        head = queue.popleft()
        in_queue.remove(head)
        productions = grammar.productions[head]
        has_update = False
        new_productions = []
        for production in productions:
            if len(production) == 1 and production[0] != head and grammar.is_non_terminal(production[0]):
                sub_productions = grammar.productions[production[0]]
                has_sub_loop = False
                for sub_production in sub_productions:
                    if len(sub_production) == 1 and sub_production[0] == production[0]:
                        has_sub_loop = True
                    new_productions.append(sub_production)
                    has_update |= grammar.add_production(head, sub_production)
                if not has_sub_loop:
                    # If A -> B and there is no B -> B, then A -> B must be removed in this production.
                    has_update = True
            else:
                new_productions.append(production)
        grammar.clean(head)
        for production in new_productions:
            grammar.add_production(head, production)
        if has_update:
            for symbol in grammar.composes.get(head, ()):
                if symbol in grammar.productions and symbol not in in_queue:
                    queue.append(symbol)
                    in_queue.add(symbol)
    return grammar
