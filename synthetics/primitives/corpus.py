import glob
from typing import Any, Optional
from collections import defaultdict
from tqdm import tqdm
from synthetics.utils import load_json


COMMON_ATTRIBUTES = {'id', 'form', 'word'}
SENTENCE_LEVEL_LAYERS = {'pos': 'morpheme', 'wsd': 'WSD', 'ner': 'NE', 'el': 'NE', 'dep': 'DP', 'srl': 'SRL'}
DOCUMENT_LEVEL_LAYERS = {'za': 'ZA', 'cr': 'CR'}


class Layer:
    def __init__(self, layer: str, data: Any, super_instance=None):
        self.super: Optional[Sentence, Document] = super_instance
        self.layer = layer
        self.data = data


class Sentence:
    def __init__(self, snt_id: str, super_instance=None):
        self.snt_id = snt_id
        self.layers = set()
        self.forms = defaultdict(set)
        self.super: Optional[Document] = super_instance
        self.annotations = defaultdict(Layer)

    @property
    def text(self):
        return sorted([(text, length) for text, length in self.forms.items()], key=lambda x: x[1])[-1]

    def get_form(self, layer: str):
        for form, layers in self.forms.items():
            if layer in layers:
                return form
        return None

    def add_form(self, form: str, layer: str):
        self.forms[form].add(layer)
        self.layers.add(layer)

    def get_annotation(self, layer: str):
        pass

    def add_annotation(self, layer: str, data: Any):
        self.annotations[layer] = Layer(layer=layer, data=data, super_instance=self)


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

    def get_annotation(self, layer: str):
        return self.annotations[layer]

    def add_annotation(self, layer: str, data: Any):
        self.annotations[layer] = Layer(layer=layer, data=data, super_instance=self)


class Corpus:
    def __init__(self, dirs: dict):
        self.dirs = dirs
        self.layers = set(dirs.keys())
        self.documents = defaultdict(Document)
        self.index = defaultdict(str)

    def __len__(self):
        return sum([len(doc) for doc in self.documents.values()])

    def __repr__(self):
        return f'<{self.__class__.__name__} → layers={self.layers}>'

    def get_document(self, doc_id: str):
        return self.documents[doc_id]

    def add_document(self, doc_id: str, instance: Document):
        self.documents[doc_id] = instance

    def get_sentence(self, snt_id: str):
        return self.documents[self.index[snt_id]].get_sentence(snt_id)

    def add_sentence(self, snt_id: str, instance: Sentence, doc_id: str):
        self.documents[doc_id].add_sentence(snt_id, instance)

    def load_files(self):
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
        return self


if __name__ == '__main__':
    search_space = 'D:\\Corpora & Language Resources\\modu-corenlp\\layers-complete\\*\\*.json'
    targets = {layer.split('\\')[-2]: layer for layer in glob.glob(search_space)}
    for l, f in targets.items():
        print(f'{l}: {f}')

    corpus = Corpus(dirs=targets).load_files()
    print(len(corpus.index))
