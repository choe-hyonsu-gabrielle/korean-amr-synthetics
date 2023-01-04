import re
from urllib.parse import unquote as decode_url
import penman
from penman import surface
from synthetics.primitives.corpus import *


class AMRHeadlessConcept:
    def __init__(self, concept_type: str, mapping: Optional[set[int]] = None):
        self.concept_type: str = concept_type
        self.attributes: dict[str, Any] = dict()  # {":relation": value}
        self.mapping: set[int] = set(sorted(mapping)) if mapping else set()

    def __repr__(self):
        return f'<{self.__class__.__name__}: "{self.concept_type}" {self.mapping}>'

    def instance_triple(self, global_idx: Any):
        return global_idx, ':instance', self.concept_type

    def alignment(self, global_idx: Any):
        return self.instance_triple(global_idx), [surface.Alignment(tuple(sorted(self.mapping)), prefix='w.')]

    def add_attribute(self, relation: str, value: Any):
        assert relation.startswith(":")
        self.attributes[relation] = value

    def product(self, global_idx: Any) -> list:
        instance = [self.instance_triple(global_idx=global_idx)]
        attributes = [(global_idx, relation, value) for relation, value in self.attributes.items()]
        return instance + attributes


class AMRNamedEntityConcept(AMRHeadlessConcept):
    def __init__(self, concept_type: str, local_idx: int, name_str: str, wiki: Optional[str] = None, mapping: Optional[set[int]] = None):
        super().__init__(concept_type=concept_type, mapping=mapping)
        self.local_idx: int = local_idx
        self.wiki = wiki if wiki and wiki != 'NA' else '-'
        self.name_str: str = re.sub(r'\s+', ' ', name_str.strip())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.concept_type} → "{self.name_str}" {self.mapping}>'

    def product(self, global_idx: Any) -> list:
        instance = [(global_idx, ':instance', self.concept_type)]
        local_idx = f'n{self.local_idx}'
        name_heads = [(local_idx, ':instance', 'name'), (global_idx, ':name', local_idx)]
        name_spans = [(local_idx, f':op{op_n + 1}', f'"{n_str}"') for op_n, n_str in enumerate(self.name_str.split())]
        wiki = [(global_idx, ':wiki', f'"{decode_url(self.wiki)}"')]
        attributes = [(global_idx, relation, value) for relation, value in self.attributes.items()]
        return instance + name_heads + name_spans + wiki + attributes


class AMRAnnotation:
    def __init__(self, annotations: Annotations):
        self.id: Optional[str] = annotations.ref_id
        self.text: Optional[str] = annotations.form
        self.metadata: dict[str, str] = dict(id=self.id, snt=self.text)
        self.annotations: Optional[Annotations] = annotations
        self.sentence: Sentence = self.annotations.super
        self.graph: AMRGraph = AMRGraph(super_instance=self)

        # initializing pipeline
        self.update_from_dep()
        self.update_from_ner()
        self.update_from_srl()

    def get_metadata(self):
        self.metadata.update({'update': timestamp()})
        return self.metadata

    def encode(self):
        return self.graph.render()

    def update_from_dep(self):
        # instances
        for word in self.annotations.dep.tolist():
            self.graph.add_instance(concept_type=word.word_form, node_idx=word.word_id, mapping={word.word_id})
        # relations
        for word in self.annotations.dep.tolist():
            head_idx: int = word.head
            relation: str = f':dep.{word.label}'
            tail_idx: int = word.word_id
            if word.head == -1:
                self.graph.top = tail_idx
            else:
                self.graph.add_relation(head_idx=head_idx, relation=relation, tail_idx=tail_idx)

    def update_from_srl(self):
        for srl in self.annotations.srl.tolist():
            _, pred_word_idx = self.sentence.span_ids_to_word_id(begin=srl.predicate.begin, end=srl.predicate.end)
            head_idx = self.graph.redirect_node(pred_word_idx)
            for arg in srl.argument:
                tail_idx = self.graph.redirect_node(arg.word_id)
                self.graph.add_relation(head_idx=head_idx, relation=f':srl.{arg.label}', tail_idx=tail_idx)
                inverted = self.graph.get_relation(tail_idx, head_idx)
                if inverted and inverted.startswith(':dep.'):
                    self.graph.del_relation(head_idx=tail_idx, tail_idx=head_idx)

    def update_from_ner(self, wikification: bool = True):
        ne_items = self.annotations.el.tolist() if wikification else self.annotations.ner.tolist()
        for ner in ne_items:
            word_begin, word_end = self.sentence.span_ids_to_word_id(begin=ner.begin, end=ner.end)
            if word_begin < word_end:
                nodes = list(range(word_begin, word_end + 1))
                new_node_idx = self.graph.amalgamate(nodes=nodes)
            elif word_begin == word_end:
                new_node_idx = word_end
            else:
                raise ValueError
            self.graph.instances[new_node_idx] = AMRNamedEntityConcept(
                concept_type=ner.label,
                local_idx=ner.id,
                name_str=ner.form,
                wiki=ner.url if wikification else None,
                mapping=self.graph.instances[new_node_idx].mapping
            )


class AMRGraph:
    def __init__(self, super_instance: AMRAnnotation):
        self.super = super_instance
        self.annotations = self.super.annotations
        self.top: Optional[str] = None
        self.instances: dict[Any, AMRHeadlessConcept] = dict()   # {node_idx: AMRHeadlessConcept}
        self.relations: dict = dict()   # {(idx1, idx2): ':relation'}

    def render(self, surface_alignment=True):
        nodes = list()
        for node_idx, concept in self.instances.items():
            nodes.extend(concept.product(global_idx=node_idx))
        edges = [(head, relation, tail) for (head, tail), relation in self.relations.items()]
        graph = penman.Graph(triples=nodes + edges, top=self.top, metadata=self.super.get_metadata())
        if surface_alignment:
            for node_idx, instance in self.instances.items():
                key, marker = instance.alignment(global_idx=node_idx)
                graph.epidata[key] = marker
        try:
            return penman.encode(graph)
        except TypeError:
            return None
        except KeyError:
            return None
        except ValueError:
            return None

    def add_instance(self, concept_type: str, node_idx: Any = None, mapping: Optional[set[int]] = None):
        mapping = set(sorted(mapping))
        self.instances[node_idx if node_idx else f'x{len(self.instances)}'] = AMRHeadlessConcept(
            concept_type=concept_type,
            mapping=mapping
        )

    def add_relation(self, head_idx: Any, relation: str, tail_idx: Any):
        assert head_idx in self.instances
        assert tail_idx in self.instances
        assert relation.startswith(':')
        self.relations[(head_idx, tail_idx)] = relation

    def get_relation(self, head_idx: Any, tail_idx: Any, include_inverted: bool = False):
        if (head_idx, tail_idx) in self.relations:
            return self.relations[(head_idx, tail_idx)]
        elif include_inverted and (tail_idx, head_idx) in self.relations:
            relation = self.relations[(tail_idx, head_idx)]
            return relation[:-3] if relation.endswith('-of') else relation + '-of'
        return None

    def del_relation(self, head_idx: Any, tail_idx: Any, include_inverted: bool = False):
        if include_inverted:
            try:
                del self.relations[(head_idx, tail_idx)]
            except KeyError:
                del self.relations[(tail_idx, head_idx)]
        else:
            del self.relations[(head_idx, tail_idx)]

    def add_attribute(self, node_idx: Any, relation: str, value: Any):
        assert node_idx in self.instances
        assert relation.startswith(':')
        self.instances[node_idx].add_attribute(relation=relation, value=value)

    def amalgamate(self, nodes: list[Any], redirect_true_node: bool = False):
        assert len(nodes) >= 2
        if redirect_true_node:
            nodes = [self.redirect_node(node_idx=n) for n in nodes]
        if len(nodes) == 2:
            return self.pairwise_merge(*nodes)
        new_node_idx = nodes.pop(0)
        node_to_merge = nodes.pop(0)
        while node_to_merge:
            new_node_idx = self.pairwise_merge(new_node_idx, node_to_merge)
            node_to_merge = nodes.pop(0) if nodes else None
        return new_node_idx

    def redirect_node(self, node_idx: Any):
        if isinstance(node_idx, (tuple, list, set)):
            for true_idx in self.instances:
                if isinstance(true_idx, (tuple, list, set)) and set(node_idx).issubset(set(true_idx)):
                    return true_idx
            return node_idx
        elif isinstance(node_idx, (int, str)):
            for true_idx in self.instances:
                if isinstance(true_idx, (tuple, list, set)) and {node_idx}.issubset(set(true_idx)):
                    return true_idx
                elif isinstance(true_idx, (int, str)) and node_idx == true_idx:
                    return true_idx
            return node_idx
        else:
            raise NotImplementedError

    def pairwise_merge(self, node_a: Any, node_b: Any):
        # backup mapping & attributes from node_a and node_b
        mapping = self.instances[node_a].mapping.union(self.instances[node_b].mapping)
        attributes = list(self.instances[node_a].attributes.items()) + list(self.instances[node_b].attributes.items())

        # remove `node_a` and `node_b` from `self.instances`
        del self.instances[node_a]
        del self.instances[node_b]

        # remove `(node_a, node_b)` from `self.relations`
        if (node_a, node_b) in self.relations:
            del self.relations[(node_a, node_b)]
        if (node_b, node_a) in self.relations:
            del self.relations[(node_b, node_a)]

        # assign new key `sorted([node_a, node_b])` as `k` and append (k, :instance, sup_inf) to `self.instances`
        new_node_idx = []
        if isinstance(node_a, (int, str)):
            new_node_idx.append(node_a)
        elif isinstance(node_a, (tuple, list, set)):
            new_node_idx.extend(list(node_a))
        else:
            raise ValueError
        if isinstance(node_b, (int, str)):
            new_node_idx.append(node_b)
        elif isinstance(node_b, (tuple, list, set)):
            new_node_idx.extend(list(node_b))
        else:
            raise ValueError
        new_node_idx = tuple(sorted(new_node_idx))
        new_concept = '_'.join([self.annotations.word(word_id) for word_id in new_node_idx])
        self.add_instance(concept_type=new_concept, node_idx=new_node_idx, mapping=mapping)

        # migration of attributes to new concept node
        for relation, value in attributes:
            self.instances[new_node_idx].add_attribute(relation=relation, value=value)

        # replace all relations either `(?, node_a)` or `(node_a, ?)` to `(?, k)` or `(?, k)`
        # replace all relations either `(?, node_b)` or `(node_b, ?)` to `(?, k)` or `(?, k)`
        for current_idx_pair, relation in list(self.relations.items()):
            current_head, current_tail = current_idx_pair
            if current_head in (node_a, node_b):
                del self.relations[current_idx_pair]
                self.add_relation(head_idx=new_node_idx, relation=relation, tail_idx=current_tail)
            if current_tail in (node_a, node_b):
                del self.relations[current_idx_pair]
                self.add_relation(head_idx=current_head, relation=relation, tail_idx=new_node_idx)

        # reset top node if necessary
        if self.top in (node_a, node_b):
            self.top = new_node_idx

        return new_node_idx


if __name__ == '__main__':
    corpus = Corpus.from_pickle('corpus.pkl')

    for i, snt in enumerate(corpus.sample_sentences(k=20, random_state=803)):
        print('\n\n')
        # print(snt.annotations.dep)
        print(snt.annotations.srl)
        print(snt.annotations.ner)
        print(snt.annotations.el)
        amr = AMRAnnotation(snt.annotations)
        print(amr.encode())
        print(amr.graph.instances)
        print(amr.graph.relations)

    """
    errors = 0
    counts = 0
    with tqdm(corpus.iter_sentences()) as progress_bar:
        for snt in progress_bar:
            progress_bar.set_description(f'errors: {errors}')
            try:
                amr = AMRAnnotation(snt.annotations)
                if amr.encode() is None:
                    errors += 1
            except KeyError:
                errors += 1
            except AssertionError:
                errors += 1
            counts += 1
    print(counts, errors)
    """
