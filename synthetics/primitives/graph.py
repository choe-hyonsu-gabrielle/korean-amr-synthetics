import penman
from penman import surface
from synthetics.primitives.corpus import *


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

    def encode(self, additional_metadata: dict = None):
        return self.graph.render()

    def update_from_dep(self):
        # instances
        for word in self.annotations.dep.tolist():
            self.graph.add_instance(concept=word.word_form, node_idx=word.word_id)
        # relations
        for word in self.annotations.dep.tolist():
            head_idx: int = word.head
            relation: str = f':{word.label}.dep'
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
                self.graph.add_relation(head_idx=head_idx, relation=f':{arg.label}.srl', tail_idx=tail_idx)
                inverted = self.graph.get_relation(tail_idx, head_idx)
                if inverted and inverted.endswith('.dep'):
                    self.graph.del_relation(head_idx=tail_idx, tail_idx=head_idx)

    def update_from_ner(self):
        for ner in self.annotations.ner.tolist():
            word_begin, word_end = self.sentence.span_ids_to_word_id(begin=ner.begin, end=ner.end)
            if word_begin < word_end:
                nodes = list(range(word_begin, word_end + 1))
                self.graph.amalgamate(nodes=nodes)


class AMRGraph:
    def __init__(self, super_instance: AMRAnnotation):
        self.super = super_instance
        self.annotations = self.super.annotations
        self.top: Optional[str] = None
        self.instances: dict = dict()   # {'node_idx': 'concept'}
        self.relations: dict = dict()   # {(idx1, idx2): ':relation'}
        self.attributes: dict = dict()  # {'node_idx': (':relation', 'value')}

    def render(self, surface_alignment=True):
        nodes = [(node_idx, ':instance', concept) for node_idx, concept in self.instances.items()]
        edges = [(head, relation, tail) for (head, tail), relation in self.relations.items()]
        attrs = [(idx, relation, value) for idx, (relation, value) in self.attributes.items()]
        graph = penman.Graph(triples=nodes + edges + attrs, top=self.top, metadata=self.super.get_metadata())
        if surface_alignment:
            for node in nodes:
                mapping = (node[0],) if isinstance(node[0], (int, str)) else node[0]
                alignment_marker = surface.Alignment(mapping, prefix='w.')
                if node in graph.epidata:
                    graph.epidata[node].append(alignment_marker)
                else:
                    graph.epidata[node] = [alignment_marker]
        try:
            return penman.encode(graph)
        except TypeError:
            return None
        except ValueError:
            return None
        except KeyError:
            return None

    def add_instance(self, concept: str, node_idx: Any = None):
        self.instances[node_idx if node_idx else f'x{len(self.instances)}'] = concept

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
        self.attributes[node_idx] = (relation, value)

    def amalgamate(self, nodes: list[Any], redirect_true_node: bool = False):
        assert len(nodes) >= 2
        if redirect_true_node:
            nodes = [self.redirect_node(node_idx=n) for n in nodes]
        if len(nodes) == 2:
            return self.pairwise_merge(*nodes)
        amalgamated_node_idx = nodes.pop(0)
        node_to_merge = nodes.pop(0)
        while node_to_merge:
            amalgamated_node_idx = self.pairwise_merge(amalgamated_node_idx, node_to_merge)
            node_to_merge = nodes.pop(0) if nodes else None
        return amalgamated_node_idx

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
        # get index of node_a and node_b
        # remove `node_a` and `node_b` from `self.instances`
        del self.instances[node_a]
        del self.instances[node_b]

        # remove `(node_a, node_b)` from `self.relations`
        if (node_a, node_b) in self.relations:
            del self.relations[(node_a, node_b)]
        if (node_b, node_a) in self.relations:
            del self.relations[(node_b, node_a)]

        # assign new key `sorted([node_a, node_b])` as `k` and append (k, :instance, sup_inf) to `self.instances`
        new_idx = []
        if isinstance(node_a, (int, str)):
            new_idx.append(node_a)
        elif isinstance(node_a, (tuple, list, set)):
            new_idx.extend(list(node_a))
        else:
            raise ValueError
        if isinstance(node_b, (int, str)):
            new_idx.append(node_b)
        elif isinstance(node_b, (tuple, list, set)):
            new_idx.extend(list(node_b))
        else:
            raise ValueError
        new_idx = tuple(sorted(new_idx))
        new_concept = '_'.join([self.annotations.word(word_id) for word_id in new_idx])
        self.add_instance(concept=new_concept, node_idx=new_idx)

        # replace all relations either `(?, node_a)` or `(node_a, ?)` to `(?, k)` or `(?, k)`
        # replace all relations either `(?, node_b)` or `(node_b, ?)` to `(?, k)` or `(?, k)`
        for current_idx_pair, relation in list(self.relations.items()):
            current_head, current_tail = current_idx_pair
            if current_head in (node_a, node_b):
                del self.relations[current_idx_pair]
                self.add_relation(head_idx=new_idx, relation=relation, tail_idx=current_tail)
            if current_tail in (node_a, node_b):
                del self.relations[current_idx_pair]
                self.add_relation(head_idx=current_head, relation=relation, tail_idx=new_idx)

        # replace all relevant attributes
        for head_node, attribute in self.attributes.items():
            # attr: {node_idx: (':relation', value)}
            if head_node in (node_a, node_b):
                del self.attributes[head_node]
                self.attributes[new_idx] = attribute

        # reset top node if necessary
        if self.top in (node_a, node_b):
            self.top = new_idx

        return new_idx


if __name__ == '__main__':
    corpus = Corpus.from_pickle('corpus.pkl')

    for i, snt in enumerate(corpus.sample_sentences(k=20, random_state=803)):
        print('\n\n')
        # print(snt.annotations.dep)
        print(snt.annotations.srl)
        print(snt.annotations.ner)
        amr = AMRAnnotation(snt.annotations)
        print(amr.encode())

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
