import re
from typing import Optional, Any
from urllib.parse import unquote as decode_url
from penman import surface


class AMRIndexFreeConcept:
    def __init__(self, concept_type: str, mapping: Optional[set[int]] = None):
        self.concept_type: str = concept_type
        self.attributes: dict[str, Any] = dict()  # {":relation": value}
        self.mapping: set[int] = set(sorted(mapping)) if mapping else set()

    def __repr__(self):
        return f'<{self.__class__.__name__}: "{self.concept_type}" {self.mapping}>'

    def head_triple(self, global_idx: Any):
        return global_idx, ':instance', self.concept_type

    def alignment(self, global_idx: Any):
        return self.head_triple(global_idx), [surface.Alignment(tuple(sorted(self.mapping)), prefix='w.')]

    def add_attribute(self, relation: str, value: Any):
        assert relation.startswith(":")
        self.attributes[relation] = value

    def product(self, global_idx: Any) -> list:
        instance = [self.head_triple(global_idx=global_idx)]
        attributes = [(global_idx, relation, value) for relation, value in self.attributes.items()]
        return instance + attributes


class AMRNamedEntityConcept(AMRIndexFreeConcept):
    def __init__(self, concept_type: str, name_idx: Any, name_str: str, wiki: Optional[str] = None,
                 mapping: Optional[set[int]] = None):
        super().__init__(concept_type=concept_type, mapping=mapping)
        self.name_idx: str = f'n{name_idx}'
        self.name_str: str = re.sub(r'\s+', ' ', name_str.strip())
        self.wiki = wiki if wiki and wiki != 'NA' else '-'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.concept_type} → "{self.name_str}" {self.mapping}>'

    def product(self, global_idx: Any) -> list:
        name_triples = [(self.name_idx, ':instance', 'name'), (global_idx, ':name', self.name_idx)]
        name_attributes = [(self.name_idx, f':op{x+1}', f'"{n_str}"') for x, n_str in enumerate(self.name_str.split())]
        wikification = [(global_idx, ':wiki', f'"{decode_url(self.wiki)}"' if self.wiki != '-' else '-')]
        return super().product(global_idx=global_idx) + name_triples + name_attributes + wikification

