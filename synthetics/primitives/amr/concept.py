import re
from typing import Optional, Any
from urllib.parse import unquote as decode_url
from penman import surface


class AMRIndexFreeConcept:
    def __init__(
            self,
            concept_type: str,
            mapping: Optional[set[int]] = None
    ):
        """
        initialize normal AMR concept node with index of node has not bound.
        you can initialize new concept node with two args as can be seen below.
        node = AMRIndexFreeConcept(concept_type="computer", mapping=(4,))
        node.product(global_idx="c")
        >> (c / computer~w.4)
        :param concept_type: str for semantic type of concept. usually lemma.
        :param mapping: Any. tuple of ints or tuples for generating alignment information.
        """
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
        attributes = [(global_idx, relation, value) for relation, value in self.attributes.items()]
        return [self.head_triple(global_idx=global_idx)] + attributes


class AMRNamedEntityConcept(AMRIndexFreeConcept):
    def __init__(
            self,
            concept_type: str,
            name_idx: Any,
            name_str: str,
            wiki: Optional[str] = None,
            mapping: Optional[set[int]] = None
    ):
        """
        initialize index-free AMR named-entity node.
        you can initialize new NE node with the args as can be seen below.
        node = AMRNamedEntityConcept(
            concept_type="country",
            name_idx=2,
            name_str="South Korea",
            wiki="https://en.wikipedia.org/wiki/South_Korea",
            mapping=(4,)
        )
        node.product(global_idx="c")
        >> (c / country~w.4
              :name (n2 / name :op1 "South" :op2 "Korea")
              :wiki "https://en.wikipedia.org/wiki/South_Korea")
        :param concept_type: str for NE type of the node. (ex. "person", "country", "thing")
        :param name_idx: Any. local idx for `name` node
        :param name_str: str of real expression in the context. (not NE type)
        :param wiki: URI of wikification
        :param mapping: Any. tuple of ints or tuples for generating alignment information.
        """
        super().__init__(concept_type=concept_type, mapping=mapping)
        self.name_idx: str = f'n{name_idx}'
        self.name_str: str = re.sub(r'\s+', ' ', name_str.strip())
        self.wiki = wiki if wiki and wiki != 'NA' else '-'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.concept_type} → "{self.name_str}" {self.mapping}>'

    def product(self, global_idx: Any) -> list:
        name_triples = [(self.name_idx, ':instance', 'name'), (global_idx, ':name', self.name_idx)]
        name_attributes = [(self.name_idx, f':op{x + 1}', f'"{n_str}"') for x, n_str in
                           enumerate(self.name_str.split())]
        wikification = [(global_idx, ':wiki', f'"{decode_url(self.wiki)}"' if self.wiki != '-' else '-')]
        return super().product(global_idx=global_idx) + name_triples + name_attributes + wikification


class AMRGenericNameConcept(AMRIndexFreeConcept):
    def __init__(
            self,
            concept_type: str,
            generic_idx: Any,
            generic_str: str,
            wiki: Optional[str] = None,
            mapping: Optional[set[int]] = None
    ):
        super().__init__(concept_type=concept_type, mapping=mapping)
        self.generic_idx: str = f'g{generic_idx}'
        self.generic_str: str = re.sub(r'\s+', ' ', generic_str.strip())
        self.wiki = wiki if wiki and wiki != 'NA' else '-'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.concept_type} → "{self.generic_str}" {self.mapping}>'

    def product(self, global_idx: Any) -> list:
        generic_triples = [
            (self.generic_idx, ':instance', '-'.join(self.generic_str.split())),
            (global_idx, ':subclass-of', self.generic_idx)
        ]
        wikification = [(global_idx, ':wiki', f'"{decode_url(self.wiki)}"' if self.wiki != '-' else '-')]
        return super().product(global_idx=global_idx) + generic_triples + wikification


class AMRTerminologyConcept(AMRIndexFreeConcept):
    def __init__(
            self,
            concept_type: str,
            term_idx: Any,
            term_str: str,
            wiki: Optional[str] = None,
            mapping: Optional[set[int]] = None
    ):
        super().__init__(concept_type=concept_type, mapping=mapping)
        self.term_idx: str = f't{term_idx}'
        self.term_str: str = re.sub(r'\s+', ' ', term_str.strip())
        self.wiki = wiki if wiki and wiki != 'NA' else '-'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.concept_type} → "{self.term_str}" {self.mapping}>'

    def product(self, global_idx: Any) -> list:
        term_triples = [(global_idx, ':instance', '-'.join(self.term_str.split()))]
        wikification = [(global_idx, ':wiki', f'"{decode_url(self.wiki)}"' if self.wiki != '-' else '-')]
        return term_triples + wikification


class AMRHaveOrgRole91Concept(AMRIndexFreeConcept):
    """
    (h / have-org-role-91
        :ARG2 (p / president))
    """
    def __init__(
            self,
            concept_type: str,
            role_idx: Any,
            role_str: str,
            wiki: Optional[str] = None,
            mapping: Optional[set[int]] = None
    ):
        super().__init__(concept_type=concept_type, mapping=mapping)
        self.role_idx: str = f'o{role_idx}'
        self.role_str: str = re.sub(r'\s+', ' ', role_str.strip())
        self.wiki = wiki if wiki and wiki != 'NA' else '-'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.concept_type} → "{self.role_str}" {self.mapping}>'

    def product(self, global_idx: Any) -> list:
        role_triples = [
            (self.role_idx, ':instance', '-'.join(self.role_str.split())),
            (global_idx, ':ARG2', self.role_idx)
        ]
        # wikification = [(global_idx, ':wiki', f'"{decode_url(self.wiki)}"' if self.wiki != '-' else '-')]
        return super().product(global_idx=global_idx) + role_triples


class AMRHaveRelRole91Concept(AMRIndexFreeConcept):
    """
    (h / have-rel-role-91
        :ARG2 (m / mother))
    """
    def __init__(
            self,
            concept_type: str,
            rel_idx: Any,
            rel_str: str,
            wiki: Optional[str] = None,
            mapping: Optional[set[int]] = None
    ):
        super().__init__(concept_type=concept_type, mapping=mapping)
        self.rel_idx: str = f'r{rel_idx}'
        self.rel_str: str = re.sub(r'\s+', ' ', rel_str.strip())
        self.wiki = wiki if wiki and wiki != 'NA' else '-'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.concept_type} → "{self.rel_str}" {self.mapping}>'

    def product(self, global_idx: Any) -> list:
        rel_triples = [
            (self.rel_idx, ':instance', '-'.join(self.rel_str.split())),
            (global_idx, ':ARG2', self.rel_idx)
        ]
        # wikification = [(global_idx, ':wiki', f'"{decode_url(self.wiki)}"' if self.wiki != '-' else '-')]
        return super().product(global_idx=global_idx) + rel_triples


class AMREmailAddressEntityConcept(AMRIndexFreeConcept):
    """
    (e / email-address-entity
       :value "president@whitehouse.gov")
    """
    def __init__(
            self,
            concept_type: str,
            email_idx: Any,
            email_str: str,
            wiki: Optional[str] = None,
            mapping: Optional[set[int]] = None
    ):
        super().__init__(concept_type=concept_type, mapping=mapping)
        self.email_idx: str = f'e{email_idx}'
        self.email_str: str = re.sub(r'\s+', ' ', email_str.strip())
        self.wiki = wiki if wiki and wiki != 'NA' else '-'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.concept_type} → "{self.email_str}" {self.mapping}>'

    def product(self, global_idx: Any) -> list:
        email_value = [(global_idx, ':value', f'"{self.email_str}"')]
        return super().product(global_idx=global_idx) + email_value


class AMRHyperlink91Concept(AMRIndexFreeConcept):
    """
    (h / hyperlink-91
       :ARG3 (u / url-entity
                :value "http://gutenberg.net.au/ebooks03/0300771h.html"))
    """
    def __init__(
            self,
            concept_type: str,
            url_idx: Any,
            url_str: str,
            wiki: Optional[str] = None,
            mapping: Optional[set[int]] = None
    ):
        super().__init__(concept_type=concept_type, mapping=mapping)
        self.url_idx: str = f'h{url_idx}'
        self.url_str: str = re.sub(r'\s+', ' ', url_str.strip())
        self.wiki = wiki if wiki and wiki != 'NA' else '-'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.concept_type} → "{self.url_str}" {self.mapping}>'

    def product(self, global_idx: Any) -> list:
        hyperlink_triples = [
            (self.url_idx, ':instance', 'url-entity'),
            (global_idx, ':ARG3', self.url_idx),
            (self.url_idx, ':value', f'"{self.url_str}"')
        ]
        return super().product(global_idx=global_idx) + hyperlink_triples
