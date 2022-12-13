from typing import Union


class Layer:
    def __init__(self):
        self.super: Union[Sentence, Document]
        self.data = None


class Sentence:
    def __init__(self):
        self.snt_id: str
        self.layers = set()
        self.text: str
        self.formset = set()
        self.super: Document
        self.snt_annotations = dict()

    def get_layer(self, layer: str):
        pass

    def add_layer(self, layer: str, instance: Layer):
        pass


class Document:
    def __init__(self):
        self.doc_id: str
        self.layers = set()
        self.sentences = dict()
        self.super: Corpus
        self.doc_annotations = dict()

    def __len__(self):
        return len(self.sentences)

    def get_sentence(self, snt_id: str):
        return self.sentences[snt_id]

    def add_sentence(self, snt_id: str, instance: Sentence):
        self.sentences[snt_id] = instance

    def get_layer(self, layer: str):
        return self.doc_annotations[layer]

    def add_layer(self, layer: str, instance: Layer):
        self.doc_annotations[layer] = instance


class Corpus:
    def __init__(self):
        self.dirs = dict()
        self.layers = set()
        self.documents = dict()
        self.snt_doc_mapping = dict()

    def __len__(self):
        return sum([len(doc) for doc in self.documents.values()])

    def get_document(self, doc_id: str):
        return self.documents[doc_id]

    def add_document(self, doc_id: str, instance: Document):
        self.documents[doc_id] = instance

    def get_sentence(self, snt_id: str):
        return self.documents[self.snt_doc_mapping[snt_id]].get_sentence(snt_id)

    def add_sentence(self, snt_id: str, instance: Sentence, doc_id: str):
        self.documents[doc_id].add_sentence(snt_id, instance)


class CorpusLoader:
    def __init__(self):
        pass
