import penman
from synthetics.primitives.corpus import *


class AMRCore:
    def __init__(self, metadata: dict):
        self.metadata = metadata
        self.top: Optional[str] = None
        self.instances: dict = dict()   # {'node_idx': 'concept'}
        self.relations: dict = dict()   # {(idx1, idx2): ':relation'}
        self.attributes: dict = dict()  # {'node_idx': (':relation', 'value')}
        self.graph = None

    def render(self):
        nodes = [(node_idx, ':instance', concept) for node_idx, concept in self.instances.items()]
        edges = [(head, relation, tail) for (head, tail), relation in self.relations.items()]
        attrs = [(idx, relation, value) for idx, (relation, value) in self.attributes.items()]
        graph = penman.Graph(triples=nodes + edges + attrs, top=self.top, metadata=self.metadata)
        self.graph = graph
        return penman.encode(graph)

    def add_instance(self, concept: str, node_idx: Any = None):
        self.instances[node_idx if node_idx else f'x{len(self.instances)}'] = concept

    def add_relation(self, head_idx: Any, relation: str, tail_idx: Any):
        assert head_idx in self.instances
        assert tail_idx in self.instances
        assert relation.startswith(':')
        self.relations[(head_idx, tail_idx)] = relation

    def add_attribute(self, node_idx: Any, relation: str, value: Any):
        assert node_idx in self.instances
        assert relation.startswith(':')
        self.attributes[node_idx] = (relation, value)


class AMRGraph:
    def __init__(self, annotations: Annotations):
        self.id: Optional[str] = annotations.ref_id
        self.text: Optional[str] = annotations.form
        self.timestamp: Optional[str] = timestamp()
        self.annotations: Optional[Annotations] = annotations
        self.core: AMRCore = AMRCore(metadata=dict(id=self.id, snt=self.text, timestamp=self.timestamp))

        # initializing pipeline
        self.dependency_to_penman()

    def encode(self):
        return self.core.render()

    def dependency_to_penman(self):
        # initial instances
        for word in self.annotations.dep.as_list():
            node_idx = word.word_id
            concept = word.word_form
            self.core.add_instance(concept, node_idx)
        # initial relations
        for word in self.annotations.dep.as_list():
            head_idx = word.head
            relation = f':{word.label}.dep'
            tail_idx = word.word_id
            if word.head == -1:
                self.core.top = tail_idx
            else:
                self.core.add_relation(head_idx, relation, tail_idx)


if __name__ == '__main__':
    corpus = Corpus.from_pickle('corpus.pkl')

    for i, snt in enumerate(corpus.sample_sentences(k=10, random_state=42)):
        print('\n\n')
        print(snt.annotations.ner)
        print(snt.annotations.dep)
        print(snt.annotations.srl)
        amr = AMRGraph(snt.annotations)
        print(amr.encode())

