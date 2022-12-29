import glob
import time
import random
from typing import Any, Union, Optional
from collections import defaultdict
from tqdm import tqdm
from synthetics.primitives.layer import *
from synthetics.utils import load_json, save_pickle, load_pickle, timestamp


SENTENCE_LEVEL_LAYERS = {'pos': 'morpheme', 'wsd': 'WSD', 'ner': 'NE', 'el': 'NE', 'dep': 'DP', 'srl': 'SRL'}
DOCUMENT_LEVEL_LAYERS = {'za': 'ZA', 'cr': 'CR'}
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


class Annotations:
    def __init__(self, super_instance=None):
        self.super: Optional[Sentence] = super_instance
        self.pos: Optional[POSLayer] = None
        self.ner: Optional[NERLayer] = None
        self.el: Optional[ELLayer] = None
        self.wsd: Optional[WSDLayer] = None
        self.dep: Optional[DEPLayer] = None
        self.srl: Optional[SRLLayer] = None
        self.za: Optional[ZALayer] = None
        self.cr: Optional[CRLayer] = None

    def __repr__(self):
        return '\n\n'.join([f'`{_var}`: {_repr}' for _var, _repr in self.__dict__.items()])

    def get(self, layer: str, default: Any = None):
        assert layer != 'super'
        return getattr(self, layer, default)

    def add(self, layer: str, instance: Union[None, POSLayer, NERLayer, ELLayer, WSDLayer, DEPLayer, SRLLayer, ZALayer, CRLayer]):
        assert layer in self.__dict__ and layer != 'super'
        setattr(self, layer, instance)

    @property
    def ref_id(self):
        return self.super.ref_id

    @property
    def form(self):
        return self.super.canonical_form

    def word(self, word_id: int):
        return self.super.word.get(word_id, None)


class Sentence:
    def __init__(self, snt_id: str, super_instance: Any = None):
        self.ref_id = snt_id
        self.forms = defaultdict(set)
        self.super: Optional[Document] = super_instance
        self.annotations = Annotations(self)
        self.index: dict[int, tuple[int, int]] = dict()  # mapping of {word_id: (begin, end)}
        self.word = dict()   # mapping of {word_id: "word_form"}

    def __repr__(self):
        return f'<{self.__class__.__name__} → id: {self.ref_id}, form ({len(self.forms)}): "{self.canonical_form}">'

    def __len__(self):
        return len(self.canonical_form)

    @property
    def pos(self) -> POSLayer:
        return self.annotations.get('pos')

    @property
    def ner(self) -> NERLayer:
        return self.annotations.get('ner')

    @property
    def el(self) -> ELLayer:
        return self.annotations.get('el')

    @property
    def wsd(self) -> WSDLayer:
        return self.annotations.get('wsd')

    @property
    def dep(self) -> DEPLayer:
        return self.annotations.get('dep')

    @property
    def srl(self) -> SRLLayer:
        return self.annotations.get('srl')

    @property
    def za(self) -> ZALayer:
        """ only returns items relevant to the sentence
        :return: list of zero-anaphora items
        """
        if self.annotations.za is not None:
            return self.annotations.get('za')
        # filter by sentence_id in predicate to get rid of irrelevant items to current Sentence
        za_list = [za for za in self.super.doc_za if za.predicate.sentence_id == self.ref_id]
        za_dict = [dict(predicate=z.predicate.__dict__, antecedent=[a.__dict__ for a in z.antecedent]) for z in za_list]
        for za_item in za_dict:
            za_item['antecedent'] = [a for a in za_item['antecedent'] if a['sentence_id'] in ('-1', self.ref_id)]
        return ZALayer(layer='za', data=[za_item for za_item in za_dict if za_item['antecedent']], super_instance=self)

    @property
    def cr(self) -> CRLayer:
        """ only returns clusters of mentions relevant to the sentence
        :return: list of clustered mentions
        """
        if self.annotations.cr is not None:
            return self.annotations.get('cr')
        valid_clusters = []
        for cr_item in self.super.doc_cr:
            intra_sentence_coreference = [m.__dict__ for m in cr_item.mention if m.sentence_id == self.ref_id]
            if len(intra_sentence_coreference) > 1:
                valid_clusters.append(intra_sentence_coreference)
        return CRLayer(layer='cr', data=[dict(mention=cluster) for cluster in valid_clusters], super_instance=self)

    @property
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

    def add_word_index(self, words: dict):
        # it is supposed to be called once only if processing on `dep`
        assert not self.word and not self.index
        self.word = {w['id']: w['form'] for w in words}
        self.index = {w['id']: (w['begin'], w['end']) for w in words}

    def word_id_to_span_ids(self, word_id: int) -> Optional[int]:
        return self.index.get(word_id, None)

    def span_ids_to_word_id(self, begin: int, end: int) -> tuple[int, int]:
        assert begin <= end
        word_begin, word_end = None, None
        for word_id, (span_begin, span_end) in self.index.items():
            if span_begin <= begin <= end <= span_end:
                return word_id, word_id
            if span_begin <= begin:
                word_begin = word_id
                continue
            if end <= span_end:
                word_end = word_id
                break
        return word_begin, word_end

    def doc_to_snt_annotation(self):
        if 'za' in self.super.annotations:
            self.annotations.add('za', self.za)
        if 'cr' in self.super.annotations:
            self.annotations.add('cr', self.cr)

    def get_annotation(self, layer: str) -> Union[None, POSLayer, NERLayer, ELLayer, WSDLayer, DEPLayer, SRLLayer, CRLayer, ZALayer]:
        return self.annotations.get(layer, None)

    def add_annotation(self, layer: str, data: Any):
        assert layer in SENTENCE_LEVEL_LAYERS
        self.annotations.add(layer, DATATYPES_BY_LAYER[layer](layer=layer, data=data, super_instance=self))


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

    @property
    def doc_cr(self) -> list[CRItem]:
        return self.get_annotation('cr').data

    @property
    def doc_za(self) -> list[ZAItem]:
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

    def sample_documents(self, k: int, random_state: int = None):
        assert k <= len(self.documents)
        random.seed(random_state)
        return [document for document in random.sample(population=list(self.documents), k=k)]

    def sample_sentences(self, k: int, random_state: int = None):
        assert k <= len(self.index)
        random.seed(random_state)
        sample_ids = random.sample(population=list(self.index), k=k)
        return [self.get_sentence(snt_id) for snt_id in sample_ids]

    def from_files(self, files: dict):
        self.dirs.update(files)
        self.layers.update(files)
        for layer, filepath in tqdm(self.dirs.items(), desc=f'{self} - loading {len(self.dirs)} files'):
            for _doc in load_json(filepath)['document']:
                doc_id = _doc['id']
                if doc_id not in self.documents:
                    self.documents[doc_id] = Document(doc_id=doc_id, super_instance=self)
                document = self.get_document(doc_id=doc_id)
                if layer in SENTENCE_LEVEL_LAYERS:
                    for _snt in _doc['sentence']:
                        snt_id = _snt['id']
                        form = _snt['form']
                        if snt_id not in document.sentences:
                            document.sentences[snt_id] = Sentence(snt_id=snt_id, super_instance=document)
                        sentence = document.get_sentence(snt_id=snt_id)
                        sentence.add_form(form=form, layer=layer)
                        data = _snt[SENTENCE_LEVEL_LAYERS[layer]]
                        sentence.add_annotation(layer=layer, data=data)
                        if layer == 'dep' and 'word' in _snt:
                            sentence.add_word_index(_snt['word'])
                        self.index[snt_id] = doc_id
                elif layer in DOCUMENT_LEVEL_LAYERS:
                    data = _doc[DOCUMENT_LEVEL_LAYERS[layer]]
                    document.add_annotation(layer=layer, data=data)
                    for _snt in _doc['sentence']:
                        snt_id = _snt['id']
                        form = _snt['form']
                        if snt_id not in document.sentences:
                            document.sentences[snt_id] = Sentence(snt_id=snt_id, super_instance=document)
                        sentence = document.get_sentence(snt_id=snt_id)
                        sentence.add_form(form=form, layer=layer)
                        self.index[snt_id] = doc_id
                        sentence.doc_to_snt_annotation()
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
        print(f'- unpickling `{filename}`, {lapse:.2f} sec lapsed, {len(loaded_corpus)} Sentences:', end=' ')
        print(loaded_corpus)
        return loaded_corpus


if __name__ == '__main__':
    # search_space = 'D:\\Corpora & Language Resources\\modu-corenlp\\layers-complete\\*\\*.json'
    search_space = '/Users/choe.hyonsu.gabrielle/modu-corenlp-essential/layers-complete/*/*.json'

    # targets = {layer.split('\\')[-2]: layer for layer in glob.glob(search_space)}
    targets = {layer.split('/')[-2]: layer for layer in glob.glob(search_space)}

    corpus = Corpus(files=targets)
    corpus.to_pickle('corpus.pkl')
    del corpus

    corpus = Corpus.from_pickle('corpus.pkl')

    for i, snt in enumerate(corpus.sample_sentences(k=10)):
        print('\n\n')
        print(snt.annotations)
