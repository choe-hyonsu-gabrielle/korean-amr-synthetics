import glob
import time
import random
import pprint
from typing import Any, Optional, Union
from collections import defaultdict
from tqdm import tqdm
from synthetics.utils import load_json, save_pickle, load_pickle, timestamp


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
        header = f'<{name_of_class} → id: "{self.super.ref_id}" ({name_of_super}), items: {len(self.data)}>'
        pformat = pprint.pformat(self.as_list(), indent=2)
        return '\n'.join([header, pformat])

    def as_list(self):
        return self.data


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

    def as_list(self) -> list[POSItem]:
        return self.data


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

    def as_list(self) -> list[NERItem]:
        return self.data


class ELItem(Item):
    def __init__(self, **kwargs):
        self.id: int = kwargs['id']
        self.form: str = kwargs['form']
        self.label: str = kwargs['label']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']
        self.k_id: str = kwargs['kid'] if 'kid' in kwargs else kwargs['k_id']
        self.wiki_id: str = kwargs['wikiid'] if 'wikiid' in kwargs else kwargs['wiki_id']
        self.url: str = kwargs['URL'] if 'URL' in kwargs else kwargs['url']


class ELLayer(Layer):
    def __init__(self, layer: str, data: list, super_instance=None):
        super().__init__(layer=layer, data=[ELItem(**d) for d in data], super_instance=super_instance)

    def as_list(self) -> list[ELItem]:
        return self.data


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

    def as_list(self) -> list[WSDItem]:
        return self.data


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

    def as_list(self) -> list[DEPItem]:
        return self.data


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

    def __repr__(self):
        return f'<{self.__class__.__name__}→\n{pprint.pformat(self.__dict__, indent=2)}>'


class SRLLayer(Layer):
    def __init__(self, layer: str, data: list, super_instance=None):
        super().__init__(layer=layer, data=[SRLItem(**d) for d in data], super_instance=super_instance)

    def as_list(self) -> list[SRLItem]:
        return self.data


class CRMention(Item):
    def __init__(self, **kwargs):
        self.sentence_id: str = kwargs['sentence_id']
        self.form: str = kwargs['form']
        self.begin: int = kwargs['begin']
        self.end: int = kwargs['end']
        self.ne_id: int = kwargs['NE_id'] if 'NE_id' in kwargs else kwargs['ne_id']


class CRItem(Item):
    def __init__(self, **kwargs):
        self.mention: list[CRMention] = [CRMention(**arg) for arg in kwargs['mention']]


class CRLayer(Layer):
    def __init__(self, layer: str, data: list, super_instance=None):
        super().__init__(layer=layer, data=[CRItem(**d) for d in data], super_instance=super_instance)

    def as_list(self) -> list[list[CRMention]]:
        return [item.mention for item in self.data]


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

    def __repr__(self):
        return f'<{self.__class__.__name__}→\n{pprint.pformat(self.__dict__, indent=2)}>'


class ZALayer(Layer):
    def __init__(self, layer: str, data: list, super_instance=None):
        super().__init__(layer=layer, data=[ZAItem(**d) for d in data], super_instance=super_instance)

    def as_list(self) -> list[ZAItem]:
        return self.data


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
    def __init__(self, **kwargs):
        self.super: Optional[Sentence] = None
        self.pos: Optional[POSLayer] = None
        self.ner: Optional[NERLayer] = None
        self.el: Optional[ELLayer] = None
        self.wsd: Optional[WSDLayer] = None
        self.dep: Optional[DEPLayer] = None
        self.srl: Optional[SRLLayer] = None
        self.za: Optional[ZALayer] = None
        self.cr: Optional[CRLayer] = None
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])

    def __repr__(self):
        return '\n\n'.join([f'`{_var}`: {_repr}' for _var, _repr in self.__dict__.items()])

    @property
    def ref_id(self):
        return self.super.ref_id

    @property
    def form(self):
        return self.super.canonical_form


class Sentence:
    def __init__(self, snt_id: str, super_instance: Any = None):
        self.ref_id = snt_id
        self.forms = defaultdict(set)
        self.super: Optional[Document] = super_instance
        self.annotations = defaultdict(Layer)
        self.index = dict()  # mapping of {word_id: (begin, end)}

    def __repr__(self):
        return f'<{self.__class__.__name__} → id: {self.ref_id}, form ({len(self.forms)}): "{self.canonical_form}">'

    def __len__(self):
        return len(self.canonical_form)

    @property
    def pos(self) -> POSLayer:
        return self.get_annotation('pos')

    @property
    def ner(self) -> NERLayer:
        return self.get_annotation('ner')

    @property
    def el(self) -> ELLayer:
        return self.get_annotation('el')

    @property
    def wsd(self) -> WSDLayer:
        return self.get_annotation('wsd')

    @property
    def dep(self) -> DEPLayer:
        return self.get_annotation('dep')

    @property
    def srl(self) -> SRLLayer:
        return self.get_annotation('srl')

    @property
    def za(self) -> ZALayer:
        """ only returns items relevant to the sentence
        :return: list of zero-anaphora items
        """
        # filter by sentence_id in predicate to get rid of irrelevant items to current Sentence
        za_list = [za for za in self.get_annotation('za').data if za.predicate.sentence_id == self.ref_id]
        za_dict = [dict(predicate=z.predicate.__dict__, antecedent=[a.__dict__ for a in z.antecedent]) for z in za_list]
        for za_item in za_dict:
            za_item['antecedent'] = [a for a in za_item['antecedent'] if a['sentence_id'] in ('-1', self.ref_id)]
        return ZALayer(layer='za', data=[za_item for za_item in za_dict if za_item['antecedent']], super_instance=self)

    @property
    def cr(self) -> CRLayer:
        """ only returns clusters of mentions relevant to the sentence
        :return: list of clustered mentions
        """
        valid_clusters = []
        for cr_item in self.get_annotation('cr').data:
            intra_sentence_coreference = [m.__dict__ for m in cr_item.mention if m.sentence_id == self.ref_id]
            if len(intra_sentence_coreference) > 1:
                valid_clusters.append(intra_sentence_coreference)
        return CRLayer(layer='cr', data=[dict(mention=cluster) for cluster in valid_clusters], super_instance=self)

    @property
    def all(self) -> Annotations:
        """ returns packed instance of all annotations: it is accessible by field names (ex. z.pos, z.ner, z.dep, ...)
        :return: a `Annotations` instance
        """
        kwargs = dict(super=self)
        kwargs.update({k: getattr(self, k) for k in self.get_layers()})
        return Annotations(**kwargs)

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

    def get_annotation(self, layer: str) -> Union[
        None, POSLayer, NERLayer, ELLayer, WSDLayer, DEPLayer, SRLLayer, CRLayer, ZALayer
    ]:
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

    @property
    def doc_cr(self) -> list[DEPItem]:
        return self.get_annotation('cr').data

    @property
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

    def sample_documents(self, k: int, random_state: int = None):
        assert k <= len(self.documents)
        random.seed(random_state)
        return [document for document in random.sample(population=list(self.documents), k=k)]

    def sample_sentences(self, k: int, random_state: int = None):
        assert k <= len(self.index)
        random.seed(random_state)
        sample_ids = random.sample(population=list(self.index), k=k)
        return [self.get_sentence(snt_id) for snt_id in sample_ids]

    def filter_sentences_by(self, len_of_text_range: tuple[int, int] = None, num_of_forms_under: int = None):
        assert len_of_text_range or num_of_forms_under
        filtered = []
        for snt_id in list(self.index):
            sentence = self.get_sentence(snt_id)
            if len(sentence.forms) > num_of_forms_under:
                continue
            if len_of_text_range[0] <= len(sentence) < len_of_text_range[1]:
                filtered.append(sentence)
        return filtered

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
        print(f'- loaded Corpus from `{filename}`, {lapse:.2f} sec lapsed, {len(loaded_corpus)} Sentences:', end=' ')
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

    for i, snt in enumerate(corpus.sample_sentences(k=30, random_state=803)):
        print('\n\n')
        print(snt.all)
