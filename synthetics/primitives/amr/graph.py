import re
import penman
from synthetics.primitives.corpus import *
from synthetics.primitives.amr.concept import AMRIndexFreeConcept, AMRNamedEntityConcept
from synthetics.rules.singletons import PeriphrasticConstructions
from synthetics.utils import ngrams


class AbstractMeaningRepresentation:
    def __init__(self, annotations: Annotations):
        self.id: Optional[str] = annotations.ref_id
        self.text: Optional[str] = annotations.form
        self.metadata: dict[str, str] = dict(id=self.id, snt=self.text)
        self.annotations: Optional[Annotations] = annotations
        self.sentence: Sentence = self.annotations.super
        self.graph: AMRGraph = AMRGraph(super_instance=self)

        # initializing pipeline
        self.pipeline = [
            self.update_from_dep,
            self.update_from_mwe,
            self.update_from_ner,
            self.update_from_srl
        ]
        for process in self.pipeline:
            process()

    def get_metadata(self):
        self.metadata.update({'update': timestamp()})
        return self.metadata

    def encode(self, surface_alignment: bool = True):
        return self.graph.render(surface_alignment=surface_alignment)

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

    def update_from_mwe(self):
        numbered_words = self.annotations.pos.numbered_items()
        for pattern in PeriphrasticConstructions(sort='simple-to-complex').get_patterns():
            queries = pattern.split()
            for numbered_ngram in ngrams(items=numbered_words, n=len(queries)):
                window = [w for _, w in numbered_ngram]
                if all([re.search(pattern=q, string=w) for q, w in zip(queries, window)]):
                    nodes = [idx for idx, _ in numbered_ngram]
                    self.graph.amalgamate(nodes, redirect_true_node=True)

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
                new_node_idx = self.graph.amalgamate(nodes=nodes, redirect_true_node=True)
            elif word_begin == word_end:
                new_node_idx = self.graph.redirect_node(word_end)
            else:
                raise ValueError
            self.graph.instances[new_node_idx] = AMRNamedEntityConcept(
                concept_type=ner.label,
                name_idx=ner.id,
                name_str=ner.form,
                wiki=ner.url if wikification else None,
                mapping=self.graph.instances[new_node_idx].mapping
            )


class AMRGraph:
    def __init__(self, super_instance: AbstractMeaningRepresentation):
        self.super = super_instance
        self.annotations = self.super.annotations
        self.top: Optional[str] = None
        self.instances: dict[Any, AMRIndexFreeConcept] = dict()   # {node_idx: AMRHeadlessConcept}
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
        self.instances[node_idx if node_idx else f'x{len(self.instances)}'] = AMRIndexFreeConcept(
            concept_type=concept_type,
            mapping=mapping
        )

    def add_relation(self, head_idx: Any, relation: str, tail_idx: Any):
        assert head_idx in self.instances
        assert tail_idx in self.instances
        assert relation.startswith(':')
        if self.redirect_node(head_idx) != self.redirect_node(tail_idx):
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

    def separate(self, node_idx: Any):
        pass

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
        if redirect_true_node:
            return self.redirect_node(new_node_idx)
        return new_node_idx

    def pairwise_merge(self, node_a: Any, node_b: Any):
        assert node_a in self.instances
        assert node_b in self.instances
        if node_a == node_b:
            return node_a

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
