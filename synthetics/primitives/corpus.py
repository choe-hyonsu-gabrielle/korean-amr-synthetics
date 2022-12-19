import glob
import time
import random
from typing import Any, Optional, NamedTuple
from collections import defaultdict
from tqdm import tqdm
from synthetics.utils import load_json, save_pickle, load_pickle, timestamp


SENTENCE_LEVEL_LAYERS = {'pos': 'morpheme', 'wsd': 'WSD', 'ner': 'NE', 'el': 'NE', 'dep': 'DP', 'srl': 'SRL'}
DOCUMENT_LEVEL_LAYERS = {'za': 'ZA', 'cr': 'CR'}


class Item:
    """ super class for individual label or sub-structural items in annotation layer """
    def __repr__(self):
        return f'<{self.__class__.__name__}→{self.__dict__}>'


class Layer:
    def __init__(self, layer: str, data: list, super_instance=None):
        """ super class for annotation layer
        :param layer: an abbreviation of layer (ex. "pos", "dep", "srl", ...)
        :param data: list object of actual data
        :param super_instance: instance of Sentence or Document
        """
        self.super: Optional[Sentence, Document] = super_instance
        self.layer = layer
        self.data = data

    def __repr__(self):
        name_of_class = self.__class__.__name__
        name_of_super = self.super.__class__.__name__
        return f'<{name_of_class} → id: "{self.super.ref_id}" ({name_of_super}, data: {self.data})>'


class POSItem(Item):
    def __init__(self, **kwargs):
        self.id: int = kwargs['id']
        self.form: str = kwargs['form']
        self.label: str = kwargs['label']
        self.word_id: int = kwargs['word_id']
        self.position: int = kwargs['position']


class POSLayer(Layer):
    def __init__(self, layer: str, data: list, super_instance=None):
        super().__init__(layer=layer, data=[POSItem(**d) for d in data], super_instance=super_instance)


class NERItem(Item):
    def __init__(self, **kwargs):
        self.id: int = kwargs['id']
        self.form: str = kwargs['form']
        self.label: str = kwargs['label']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']


class NERLayer(Layer):
    def __init__(self, layer: str, data: list, super_instance=None):
        super().__init__(layer=layer, data=[NERItem(**d) for d in data], super_instance=super_instance)


class ELItem(Item):
    def __init__(self, **kwargs):
        self.id: int = kwargs['id']
        self.form: str = kwargs['form']
        self.label: str = kwargs['label']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']
        self.k_id: str = kwargs['kid']
        self.wiki_id: str = kwargs['wikiid']
        self.url: str = kwargs['URL']


class ELLayer(Layer):
    def __init__(self, layer: str, data: list, super_instance=None):
        super().__init__(layer=layer, data=[ELItem(**d) for d in data], super_instance=super_instance)


class WSDItem(Item):
    def __init__(self, **kwargs):
        self.word: str = kwargs['word']
        self.sense_id: int = kwargs['sense_id']
        self.pos: str = kwargs['pos']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']
        self.word_id: int = kwargs['word_id']


class WSDLayer(Layer):
    def __init__(self, layer: str, data: list, super_instance=None):
        super().__init__(layer=layer, data=[WSDItem(**d) for d in data], super_instance=super_instance)


class DEPItem(Item):
    def __init__(self, **kwargs):
        self.word_id: int = kwargs['word_id']
        self.word_form: str = kwargs['word_form']
        self.head: int = kwargs['head']
        self.label: str = kwargs['label']
        self.dependent: list[int] = kwargs['dependent']


class DEPLayer(Layer):
    def __init__(self, layer: str, data: list, super_instance=None):
        super().__init__(layer=layer, data=[DEPItem(**d) for d in data], super_instance=super_instance)


class SRLPredicate(Item):
    def __init__(self, **kwargs):
        self.form: str = kwargs['form']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']
        self.lemma: str = kwargs['lemma']


class SRLArgument(Item):
    def __init__(self, **kwargs):
        self.form: str = kwargs['form']
        self.label: str = kwargs['label']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']
        self.word_id: int = kwargs['word_id']


class SRLItem(Item):
    def __init__(self, **kwargs):
        self.predicate: SRLPredicate = SRLPredicate(**kwargs['predicate'])
        self.argument: list[SRLArgument] = [SRLArgument(**arg) for arg in kwargs['argument']]


class SRLLayer(Layer):
    def __init__(self, layer: str, data: list, super_instance=None):
        super().__init__(layer=layer, data=[SRLItem(**d) for d in data], super_instance=super_instance)


class CRMention(Item):
    def __init__(self, **kwargs):
        self.sentence_id: str = kwargs['sentence_id']
        self.form: str = kwargs['form']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']
        self.ne_id: int = kwargs['NE_id']


class CRItem(Item):
    def __init__(self, **kwargs):
        self.mention: list[CRMention] = [CRMention(**arg) for arg in kwargs['mention']]


class CRLayer(Layer):
    def __init__(self, layer: str, data: list, super_instance=None):
        super().__init__(layer=layer, data=[CRItem(**d) for d in data], super_instance=super_instance)


class ZAPredicate(Item):
    def __init__(self, **kwargs):
        self.form: str = kwargs['form']
        self.sentence_id: str = kwargs['sentence_id']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']


class ZAAntecedent(Item):
    def __init__(self, **kwargs):
        self.form: str = kwargs['form']
        self.type: str = kwargs['type']
        self.sentence_id: str = kwargs['sentence_id']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']


class ZAItem(Item):
    def __init__(self, **kwargs):
        self.predicate: ZAPredicate = ZAPredicate(**kwargs['predicate'])
        self.antecedent: list[ZAAntecedent] = [ZAAntecedent(**a_kwargs) for a_kwargs in kwargs['antecedent']]


class ZALayer(Layer):
    def __init__(self, layer: str, data: list, super_instance=None):
        super().__init__(layer=layer, data=[ZAItem(**d) for d in data], super_instance=super_instance)


DATATYPES_BY_LAYER = {
    'pos': POSLayer,
    'wsd': WSDLayer,
    'ner': NERLayer,
    'el': ELLayer,
    'dep': DEPLayer,
    'srl': SRLLayer,
    'za': ZALayer,
    'cr': CRLayer
}


class AnnotatedLayers(NamedTuple):
    """ namedtuple for a return of Sentence.all() """
    pos: list[POSItem] = None
    ner: list[NERItem] = None
    el: list[ELItem] = None
    wsd: list[WSDItem] = None
    dep: list[DEPItem] = None
    srl: list[SRLItem] = None
    za: list[ZAItem] = None
    cr: list[list[CRMention]] = None


class Sentence:
    def __init__(self, snt_id: str, super_instance: Any = None):
        self.ref_id = snt_id
        self.forms = defaultdict(set)
        self.super: Optional[Document] = super_instance
        self.annotations = defaultdict(Layer)
        self.index = dict()  # mapping of {word_id: (begin, end)}

    def __repr__(self):
        return f'<{self.__class__.__name__} → id: {self.ref_id}, form ({len(self.forms)}): "{self.canonical_form()}">'

    def pos(self) -> list[POSItem]:
        return self.get_annotation('pos').data

    def ner(self) -> list[NERItem]:
        return self.get_annotation('ner').data

    def el(self) -> list[ELItem]:
        return self.get_annotation('el').data

    def wsd(self) -> list[WSDItem]:
        return self.get_annotation('wsd').data

    def dep(self) -> list[DEPItem]:
        return self.get_annotation('dep').data

    def srl(self) -> list[SRLItem]:
        return self.get_annotation('srl').data

    def za(self) -> list[ZAItem]:
        """ only returns items relevant to the sentence
        :return: list of zero-anaphora items
        """
        # filter by sentence_id in predicate to get rid of irrelevant items to current Sentence
        za_list = [za for za in self.get_annotation('za').data if za.predicate.sentence_id == self.ref_id]
        za_dict = [dict(predicate=z.predicate.__dict__, antecedent=[a.__dict__ for a in z.antecedent]) for z in za_list]
        for za_item in za_dict:
            za_item['antecedent'] = [a for a in za_item['antecedent'] if a['sentence_id'] in ('-1', self.ref_id)]
        return [ZAItem(**za_item) for za_item in za_dict if za_item['antecedent']]

    def cr(self) -> list[list[CRMention]]:
        """ only returns clusters of mentions relevant to the sentence
        :return: list of clustered mentions
        """
        valid_clusters = []
        for cr_item in self.get_annotation('cr').data:
            intra_sentence_coreference = [m for m in cr_item.mention if m.sentence_id == self.ref_id]
            if len(intra_sentence_coreference) > 1:
                valid_clusters.append(intra_sentence_coreference)
        return valid_clusters

    def all(self) -> AnnotatedLayers:
        """ returns namedtuple of all annotations: it is accessible by field names (ex. z.pos, z.ner, z.dep, ...)
        :return: a namedtuple
        """
        return AnnotatedLayers(**{k: getattr(self, k)() for k in self.get_layers()})

    def canonical_form(self) -> str:
        if len(self.forms) == 1:
            return list(self.forms)[0]
        return sorted([(text, len(layers)) for text, layers in self.forms.items()], key=lambda x: x[1])[-1][0]

    def get_form(self, layer: str) -> Optional[str]:
        for form, layers in self.forms.items():
            if layer in layers:
                return form
        return None

    def add_form(self, form: str, layer: str):
        self.forms[form].add(layer)

    def add_index(self, words: dict):
        if self.index:
            assert self.index == {w['id']: (w['begin'], w['end']) for w in words}
        else:
            self.index = {w['id']: (w['begin'], w['end']) for w in words}

    def word_id_to_span_ids(self, word_id: int) -> Optional[int]:
        return self.index.get(word_id, None)

    def span_ids_to_word_id(self, begin: int, end: int) -> Optional[int]:
        for word_id, (_begin, _end) in self.index.items():
            if _begin <= begin <= end <= _end:
                return word_id
        return None

    def get_annotation(self, layer: str) -> Layer:
        if layer in SENTENCE_LEVEL_LAYERS:
            return self.annotations.get(layer, None)
        elif layer in DOCUMENT_LEVEL_LAYERS:
            return self.super.annotations.get(layer, None)
        else:
            raise KeyError

    def add_annotation(self, layer: str, data: Any):
        assert layer in SENTENCE_LEVEL_LAYERS
        self.annotations[layer] = DATATYPES_BY_LAYER[layer](layer=layer, data=data, super_instance=self)

    def get_layers(self) -> list[str]:
        return list(set(list(self.annotations) + list(self.super.annotations)))


class Document:
    def __init__(self, doc_id: str, super_instance=None):
        self.ref_id = doc_id
        self.sentences = defaultdict(Sentence)
        self.super: Optional[Corpus] = super_instance
        self.annotations = defaultdict(Layer)

    def __len__(self):
        return len(self.sentences)

    def get_sentence(self, snt_id: str) -> Sentence:
        return self.sentences.get(snt_id, None)

    def add_sentence(self, snt_id: str, instance: Sentence):
        self.sentences[snt_id] = instance

    def get_annotation(self, layer: str) -> Layer:
        assert layer in DOCUMENT_LEVEL_LAYERS
        return self.annotations.get(layer, None)

    def add_annotation(self, layer: str, data: Any):
        assert layer in DOCUMENT_LEVEL_LAYERS
        self.annotations[layer] = DATATYPES_BY_LAYER[layer](layer=layer, data=data, super_instance=self)

    def doc_cr(self) -> list[DEPItem]:
        return self.get_annotation('cr').data

    def doc_za(self) -> list[SRLItem]:
        return self.get_annotation('za').data


class Corpus:
    def __init__(self, files: dict = None):
        self.dirs = dict()
        self.layers = set()
        self.documents = defaultdict(Document)
        self.index = defaultdict(str)  # mapping of snt_id to doc_id
        self.update = None

        if files:
            self.from_files(files=files)

    def __len__(self):
        return len(self.index)  # length of all sentences

    def __repr__(self):
        return f'<{self.__class__.__name__} → id: {id(self)}, update: {self.update}, layers: {tuple(self.layers)}>'

    def get_document(self, doc_id: str) -> Document:
        return self.documents.get(doc_id, None)

    def add_document(self, doc_id: str, instance: Document):
        self.documents[doc_id] = instance

    def get_sentence(self, snt_id: str) -> Optional[Sentence]:
        doc_id = self.index.get(snt_id, None)
        if doc_id:
            return self.documents[doc_id].get_sentence(snt_id)
        return None

    def add_sentence(self, snt_id: str, instance: Sentence, doc_id: str):
        self.documents[doc_id].add_sentence(snt_id, instance)

    def iter_documents(self):
        return (document for document in self.documents)

    def iter_sentences(self):
        return (self.get_sentence(snt_id) for snt_id in self.index)

    def sample_documents(self, k: int):
        assert k <= len(self.documents)
        return [document for document in random.sample(population=list(self.documents), k=k)]

    def sample_sentences(self, k: int):
        assert k <= len(self.index)
        sample_ids = random.sample(population=list(self.index), k=k)
        return [self.get_sentence(snt_id) for snt_id in sample_ids]

    def from_files(self, files: dict):
        self.dirs.update(files)
        self.layers.update(files)
        for layer, filepath in tqdm(self.dirs.items(), desc=f'{self}: loading {len(self.dirs)} files'):
            for _doc in load_json(filepath)['document']:
                doc_id = _doc['id']
                if doc_id not in self.documents:
                    self.documents[doc_id] = Document(doc_id=doc_id, super_instance=self)
                document = self.get_document(doc_id=doc_id)
                if layer in SENTENCE_LEVEL_LAYERS:
                    for _snt in _doc['sentence']:
                        snt_id, form, data = _snt['id'], _snt['form'], _snt[SENTENCE_LEVEL_LAYERS[layer]]
                        if snt_id not in document.sentences:
                            document.sentences[snt_id] = Sentence(snt_id=snt_id, super_instance=document)
                        sentence = document.get_sentence(snt_id=snt_id)
                        sentence.add_form(form=form, layer=layer)
                        sentence.add_annotation(layer=layer, data=data)
                        self.index[snt_id] = doc_id
                elif layer in DOCUMENT_LEVEL_LAYERS:
                    for _snt in _doc['sentence']:
                        snt_id, form = _snt['id'], _snt['form']
                        if snt_id not in document.sentences:
                            document.sentences[snt_id] = Sentence(snt_id=snt_id, super_instance=document)
                        sentence = document.get_sentence(snt_id=snt_id)
                        if 'word' in _snt:
                            sentence.add_index(_snt['word'])
                        sentence.add_form(form=form, layer=layer)
                        self.index[snt_id] = doc_id
                    data = _doc[DOCUMENT_LEVEL_LAYERS[layer]]
                    document.add_annotation(layer=layer, data=data)
                else:
                    raise ValueError(f'`{layer}` is unsupported annotation type: {list(DATATYPES_BY_LAYER)}')
        # timestamp
        self.update = timestamp()
        return self

    def to_pickle(self, filename):
        # timestamp
        self.update = timestamp()
        save_pickle(filename=filename, instance=self)

    @staticmethod
    def from_pickle(filename):
        start = time.time()
        loaded_corpus: Corpus = load_pickle(filename)
        lapse = time.time() - start
        print(f'- loaded Corpus instance from `{filename}`, {lapse} sec lapsed for {len(loaded_corpus)} Sentences')
        print(loaded_corpus)
        return loaded_corpus


if __name__ == '__main__':
    # search_space = 'D:\\Corpora & Language Resources\\modu-corenlp\\layers-complete\\*\\*.json'
    search_space = '/Users/choe.hyonsu.gabrielle/modu-corenlp-essential/layers-complete/*/*.json'

    # targets = {layer.split('\\')[-2]: layer for layer in glob.glob(search_space)}
    targets = {layer.split('/')[-2]: layer for layer in glob.glob(search_space)}

    # corpus = Corpus(files=targets)
    # corpus.to_pickle('corpus.pkl')
    # del corpus

    corpus = Corpus.from_pickle('corpus.pkl')

    import pprint
    for i, snt in enumerate(corpus.sample_sentences(k=20)):
        print('\n')
        print(snt)
        for t in snt.all():
            pprint.pprint(t)
