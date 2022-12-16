import glob
import time
import datetime
from typing import Any, Optional
from collections import defaultdict
from tqdm import tqdm
from synthetics.utils import load_json, save_pickle, load_pickle


COMMON_ATTRIBUTES = {'id', 'form', 'word'}
SENTENCE_LEVEL_LAYERS = {'pos': 'morpheme', 'wsd': 'WSD', 'ner': 'NE', 'el': 'NE', 'dep': 'DP', 'srl': 'SRL'}
DOCUMENT_LEVEL_LAYERS = {'za': 'ZA', 'cr': 'CR'}


class Layer:
    def __init__(self, layer: str, data: Any, super_instance=None):
        self.super: Optional[Sentence, Document] = super_instance
        self.layer = layer
        self.data = data


class POSItem:
    def __init__(self, **kwargs):
        self.id: int = kwargs['id']
        self.form: str = kwargs['form']
        self.label: str = kwargs['label']
        self.word_id: int = kwargs['word_id']
        self.position: int = kwargs['position']


class POSLayer(Layer):
    def __init__(self, layer: str, data: Any, super_instance=None):
        super().__init__(layer=layer, data=[POSItem(**d) for d in data], super_instance=super_instance)


class NERItem:
    def __init__(self, **kwargs):
        self.id: int = kwargs['id']
        self.form: str = kwargs['form']
        self.label: str = kwargs['label']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']


class NERLayer(Layer):
    def __init__(self, layer: str, data: Any, super_instance=None):
        super().__init__(layer=layer, data=[NERItem(**d) for d in data], super_instance=super_instance)


class ELItem:
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
    def __init__(self, layer: str, data: Any, super_instance=None):
        super().__init__(layer=layer, data=[ELItem(**d) for d in data], super_instance=super_instance)


class WSDItem:
    def __init__(self, **kwargs):
        self.word: str = kwargs['word']
        self.sense_id: int = kwargs['sense_id']
        self.pos: str = kwargs['pos']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']
        self.word_id: int = kwargs['word_id']


class WSDLayer(Layer):
    def __init__(self, layer: str, data: Any, super_instance=None):
        super().__init__(layer=layer, data=[WSDItem(**d) for d in data], super_instance=super_instance)


class DEPItem:
    def __init__(self, **kwargs):
        self.word_id: int = kwargs['word_id']
        self.word_form: str = kwargs['word_form']
        self.head: int = kwargs['head']
        self.label: str = kwargs['label']
        self.dependent: list[int] = kwargs['dependent']


class DEPLayer(Layer):
    def __init__(self, layer: str, data: Any, super_instance=None):
        super().__init__(layer=layer, data=[DEPItem(**d) for d in data], super_instance=super_instance)


class SRLPredicate:
    def __init__(self, **kwargs):
        self.form: str = kwargs['form']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']
        self.lemma: str = kwargs['lemma']


class SRLArgument:
    def __init__(self, **kwargs):
        self.form: str = kwargs['form']
        self.label: str = kwargs['label']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']
        self.word_id: int = kwargs['word_id']


class SRLItem:
    def __init__(self, **kwargs):
        self.predicate: SRLPredicate = SRLPredicate(**kwargs['predicate'])
        self.argument: list[SRLArgument] = [SRLArgument(**arg) for arg in kwargs['argument']]


class SRLLayer(Layer):
    def __init__(self, layer: str, data: Any, super_instance=None):
        super().__init__(layer=layer, data=[SRLItem(**d) for d in data], super_instance=super_instance)


class CRMention:
    def __init__(self, **kwargs):
        self.sentence_id: str = kwargs['sentence_id']
        self.form: str = kwargs['form']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']
        self.ne_id: int = kwargs['NE_id']


class CRItem:
    def __init__(self, **kwargs):
        self.mention: list[CRMention] = [CRMention(**arg) for arg in kwargs['mention']]


class CRLayer(Layer):
    def __init__(self, layer: str, data: Any, super_instance=None):
        super().__init__(layer=layer, data=[CRItem(**d) for d in data], super_instance=super_instance)


class ZAPredicate:
    def __init__(self, **kwargs):
        self.form: str = kwargs['form']
        self.sentence_id: str = kwargs['sentence_id']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']


class ZAAntecedent:
    def __init__(self, **kwargs):
        self.form: str = kwargs['form']
        self.type: str = kwargs['type']
        self.sentence_id: str = kwargs['sentence_id']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']


class ZAItem:
    def __init__(self, **kwargs):
        self.predicate: ZAPredicate = ZAPredicate(**kwargs['predicate'])
        self.antecedent: list[ZAAntecedent] = [ZAAntecedent(**arg) for arg in kwargs['antecedent']]


class ZALayer(Layer):
    def __init__(self, layer: str, data: Any, super_instance=None):
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


class Sentence:
    def __init__(self, snt_id: str, super_instance=None):
        self.snt_id = snt_id
        self.layers = set()
        self.forms = defaultdict(set)
        self.super: Optional[Document] = super_instance
        self.annotations = defaultdict(Layer)

    # @property
    def get_canonical_form(self):
        if len(self.forms) == 1:
            return list(self.forms)[0]
        return sorted([(text, length) for text, length in self.forms.items()], key=lambda x: x[1])[-1]

    def get_form(self, layer: str) -> Optional[str]:
        for form, layers in self.forms.items():
            if layer in layers:
                return form
        return None

    def add_form(self, form: str, layer: str):
        self.forms[form].add(layer)
        self.layers.add(layer)

    def get_annotation(self, layer: str) -> Layer:
        return self.annotations[layer]

    def add_annotation(self, layer: str, data: Any):
        self.annotations[layer] = DATATYPES_BY_LAYER[layer](layer=layer, data=data, super_instance=self)


class Document:
    def __init__(self, doc_id: str, super_instance=None):
        self.doc_id = doc_id
        self.layers = set()
        self.sentences = defaultdict(Sentence)
        self.super: Optional[Corpus] = super_instance
        self.annotations = defaultdict(Layer)

    def __len__(self):
        return len(self.sentences)

    def get_sentence(self, snt_id: str):
        return self.sentences[snt_id]

    def add_sentence(self, snt_id: str, instance: Sentence):
        self.sentences[snt_id] = instance

    def get_annotation(self, layer: str) -> Layer:
        return self.annotations[layer]

    def add_annotation(self, layer: str, data: Any):
        self.annotations[layer] = DATATYPES_BY_LAYER[layer](layer=layer, data=data, super_instance=self)


class Corpus:
    def __init__(self):
        self.dirs = dict()
        self.layers = set()
        self.documents = defaultdict(Document)
        self.index = defaultdict(str)
        self.update = None

    def __len__(self):
        return sum([len(doc) for doc in self.documents.values()])

    def __repr__(self):
        return f'<{self.__class__.__name__} → id: {id(self)}, update: {self.update}, layers: {tuple(self.layers)}>'

    def get_document(self, doc_id: str):
        return self.documents[doc_id]

    def add_document(self, doc_id: str, instance: Document):
        self.documents[doc_id] = instance

    def get_sentence(self, snt_id: str):
        return self.documents[self.index[snt_id]].get_sentence(snt_id)

    def add_sentence(self, snt_id: str, instance: Sentence, doc_id: str):
        self.documents[doc_id].add_sentence(snt_id, instance)

    def from_files(self, files: dict):
        self.dirs.update(files)
        self.layers.update(files.keys())
        for layer, filepath in tqdm(self.dirs.items(), desc=f'{self}: loading {len(self.dirs)} files'):
            _corpus = load_json(filepath)
            for _doc in _corpus['document']:
                doc_id = _doc['id']
                if doc_id not in self.documents:
                    self.documents[doc_id] = Document(doc_id=doc_id, super_instance=self)
                document = self.get_document(doc_id=doc_id)
                document.layers.add(layer)
                if layer in SENTENCE_LEVEL_LAYERS:
                    for _snt in _doc['sentence']:
                        snt_id = _snt['id']
                        form = _snt['form']
                        data = _snt[SENTENCE_LEVEL_LAYERS[layer]]
                        if snt_id not in document.sentences:
                            document.sentences[snt_id] = Sentence(snt_id=snt_id, super_instance=document)
                        sentence = document.get_sentence(snt_id=snt_id)
                        sentence.add_form(form=form, layer=layer)
                        sentence.add_annotation(layer=layer, data=data)
                        self.index[snt_id] = doc_id
                elif layer in DOCUMENT_LEVEL_LAYERS:
                    for _snt in _doc['sentence']:
                        snt_id = _snt['id']
                        form = _snt['form']
                        if snt_id not in document.sentences:
                            document.sentences[snt_id] = Sentence(snt_id=snt_id, super_instance=document)
                        sentence = document.get_sentence(snt_id=snt_id)
                        sentence.add_form(form=form, layer=layer)
                        self.index[snt_id] = doc_id
                    data = _doc[DOCUMENT_LEVEL_LAYERS[layer]]
                    document.add_annotation(layer=layer, data=data)
                else:
                    raise ValueError('Unsupported annotation type.')
        # timestamp
        self.update = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        return self

    def to_pickle(self, filename):
        # timestamp
        self.update = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        save_pickle(filename=filename, instance=self)

    @staticmethod
    def from_pickle(filename):
        loaded_corpus: Corpus = load_pickle(filename)
        return loaded_corpus


if __name__ == '__main__':
    # search_space = 'D:\\Corpora & Language Resources\\modu-corenlp\\layers-complete\\*\\*.json'
    search_space = '/Users/choe.hyonsu.gabrielle/modu-corenlp-essential/layers-complete/*/*.json'

    # targets = {layer.split('\\')[-2]: layer for layer in glob.glob(search_space)}
    targets = {layer.split('/')[-2]: layer for layer in glob.glob(search_space)}

    for n, f in targets.items():
        print(f'- {n}: {f}')

    corpus = Corpus().from_files(files=targets)
    corpus.to_pickle('corpus.pkl')
    del corpus

    start = time.time()
    corpus = Corpus.from_pickle('corpus.pkl')
    print(time.time() - start)

    print(corpus)
    print(len(corpus.index))
    print(corpus.dirs)


