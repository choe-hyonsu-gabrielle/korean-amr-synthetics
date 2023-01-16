from typing import Literal
from collections import defaultdict
from functools import cache
from synthetics.rules.periphrastic import PERIPHRASTIC_CONSTRUCTIONS


def prioritize(rules: dict[str, str], sort: Literal['simple-to-complex', 'complex-to-simple'] = 'simple-to-complex'):
    assert sort in ('simple-to-complex', 'complex-to-simple')
    assert len(rules.keys()) == len(rules.values())
    reverse = False if sort == 'simple-to-complex' else True
    ngram_ranks = defaultdict(list)
    for key, rule in rules.items():
        ngram_ranks[len(rule.split())].append(key)
    for n in ngram_ranks:
        ngram_ranks[n] = sorted(ngram_ranks[n], key=lambda k: len(rules[k]), reverse=reverse)
    n_order = sorted(list(ngram_ranks.keys()), reverse=reverse)
    priority = []
    for n in n_order:
        priority.extend(ngram_ranks[n])
    return priority


class PeriphrasticConstructions(object):
    instance = None
    intact = True

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, sort: Literal['simple-to-complex', 'complex-to-simple']):
        if PeriphrasticConstructions.intact:
            self.ruleset = PERIPHRASTIC_CONSTRUCTIONS
            self.sort = sort
            self.priority = prioritize(self.ruleset, sort=sort)
            PeriphrasticConstructions.intact = False

    @cache
    def get_patterns(self):
        return [self.ruleset[key] for key in self.priority]


if __name__ == '__main__':
    pc = PeriphrasticConstructions(sort='simple-to-complex')
    print(pc.sort)
