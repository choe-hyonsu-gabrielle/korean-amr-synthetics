import penman
from penman import surface
from synthetics.primitives.corpus import *


class AMRGraph:
    def __init__(self, annotations: Annotations):
        self.annotations = annotations
        self.top: Optional[str] = None
        self.instances: dict = dict()   # {'node_idx': 'concept'}
        self.relations: dict = dict()   # {(idx1, idx2): ':relation'}
        self.attributes: dict = dict()  # {'node_idx': (':relation', 'value')}

    def render(self, metadata=None, surface_alignment=True):
        nodes = [(node_idx, ':instance', concept) for node_idx, concept in self.instances.items()]
        edges = [(head, relation, tail) for (head, tail), relation in self.relations.items()]
        attrs = [(idx, relation, value) for idx, (relation, value) in self.attributes.items()]
        graph = penman.Graph(triples=nodes + edges + attrs, top=self.top, metadata=metadata)
        if surface_alignment:
            for node in nodes:
                mapping = (node[0],) if isinstance(node[0], (int, str)) else node[0]
                alignment_marker = surface.Alignment(mapping, prefix='w.')
                if node in graph.epidata:
                    graph.epidata[node].append(alignment_marker)
                else:
                    graph.epidata[node] = [alignment_marker]
        return penman.encode(graph)

    def add_instance(self, concept: str, node_idx: Any = None):
        self.instances[node_idx if node_idx else f'x{len(self.instances)}'] = concept

    def add_relation(self, head_idx: Any, relation: str, tail_idx: Any):
        assert head_idx in self.instances
        assert tail_idx in self.instances
        assert relation.startswith(':')
        self.relations[(head_idx, tail_idx)] = relation

    def get_relation(self, head_idx: Any, tail_idx: Any):
        if (head_idx, tail_idx) in self.relations:
            return self.relations[(head_idx, tail_idx)]
        elif (tail_idx, head_idx) in self.relations:
            relation = self.relations[(tail_idx, head_idx)]
            return relation[:-3] if relation.endswith('-of') else relation + '-of'
        return None

    def add_attribute(self, node_idx: Any, relation: str, value: Any):
        assert node_idx in self.instances
        assert relation.startswith(':')
        self.attributes[node_idx] = (relation, value)

    def amalgamate(self):
        pass

    def pairwise_merge(self, node_pair: tuple, ownership: Any):
        assert len(node_pair) == 2
        assert ownership in node_pair
        assert self.get_relation(*node_pair)

        # get index of superior and inferior
        stack = list(node_pair)
        superior = stack.pop(node_pair.index(ownership))
        inferior = stack.pop()
        assert len(stack) == 0

        # remove `superior` and `inferior` from `self.instances`
        del self.instances[superior]
        del self.instances[inferior]

        # assign new key `sorted([superior, inferior])` as `k` and append (k, :instance, sup_inf) to `self.instances`
        new_idx = []
        if isinstance(superior, (int, str)):
            new_idx.append(superior)
        else:
            new_idx.extend(list(superior))
        if isinstance(inferior, (int, str)):
            new_idx.append(inferior)
        else:
            new_idx.extend(list(inferior))
        new_idx = sorted(new_idx)
        new_concept = '_'.join([self.annotations.word(word_id) for word_id in new_idx])
        self.add_instance(concept=new_concept, node_idx=new_idx)

        # remove `(superior, inferior)` from `self.relations`
        del self.relations[(superior, inferior)]

        # replace all relations either `(?, superior)` or `(superior, ?)` to `(?, k)` or `(?, k)`
        # replace all relations either `(?, inferior)` or `(inferior, ?)` to `(?, k)` or `(?, k)`
        for old_idx_pair, relation in self.relations.items():
            old_head, old_tail = old_idx_pair
            if old_head in (superior, inferior):
                self.add_relation(head_idx=new_idx, relation=relation, tail_idx=old_tail)
                del self.relations[old_idx_pair]
            if old_tail in (superior, inferior):
                self.add_relation(head_idx=old_head, relation=relation, tail_idx=new_idx)
                del self.relations[old_idx_pair]

        # reset top node if necessary
        if self.top in (superior, inferior):
            self.top = new_idx

        return new_idx


class AMRAnnotation:
    def __init__(self, annotations: Annotations):
        self.id: Optional[str] = annotations.ref_id
        self.text: Optional[str] = annotations.form
        self.annotations: Optional[Annotations] = annotations
        self.sentence = self.annotations.super
        self.graph: AMRGraph = AMRGraph(annotations=annotations)

        # initializing pipeline
        self.parse_to_penman()
        self.update_from_srl()
        self.merge_test()

    def encode(self, additional_metadata: dict = None):
        metadata = dict(id=self.id, update=timestamp(), snt=self.text)
        if additional_metadata:
            metadata.update(additional_metadata)
        return self.graph.render(metadata=metadata)

    def parse_to_penman(self):
        # instances
        for word in self.annotations.dep.as_list():
            node_idx = word.word_id
            concept = word.word_form
            self.graph.add_instance(concept, node_idx)
        # relations
        for word in self.annotations.dep.as_list():
            head_idx = word.head
            relation = f':{word.label}.dep'
            tail_idx = word.word_id
            if word.head == -1:
                self.graph.top = tail_idx
            else:
                self.graph.add_relation(head_idx, relation, tail_idx)

    def update_from_srl(self):
        for srl in self.annotations.srl.as_list():
            predicate_word_id = self.sentence.span_ids_to_word_id(begin=srl.predicate.begin, end=srl.predicate.end)
            for arg in srl.argument:
                self.graph.relations[(predicate_word_id, arg.word_id)] = f':{arg.label}.srl'

    def merge_test(self):
        if self.id == 'NWRW1800000028.263.6.3':
            self.graph.pairwise_merge(node_pair=(9, 8), ownership=9)


if __name__ == '__main__':
    corpus = Corpus.from_pickle('corpus.pkl')

    for i, snt in enumerate(corpus.sample_sentences(k=10, random_state=42)):
        print('\n\n')
        print(snt.annotations.ner)
        print(snt.annotations.dep)
        print(snt.annotations.srl)
        amr = AMRAnnotation(snt.annotations)
        print(amr.encode())

