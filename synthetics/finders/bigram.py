from synthetics.utils import subgroups
from synthetics.primitives.corpus import Corpus


class Morpheme:
    def __init__(self, form: str, pos: str):
        self.form = form
        self.pos = pos
        self.freq: int = 1

    def anonymize_form(self):
        pass


class Vocabulary:
    def __init__(self):
        self.lexicon = dict()

    def add_vocab(self, form: str, pos: str):
        if (form, pos) in self.lexicon:
            self.lexicon[(form, pos)].freq += 1
        else:
            self.lexicon[(form, pos)] = Morpheme(form, pos)

    def get_vocab(self, form: str, pos: str):
        return self.lexicon.get((form, pos), None)


class BigramPattern:
    def __init__(self, former: list[tuple], latter: list[tuple]):
        self.freq = 0
        self.expressions = dict()


class BigramPatternFinder:
    def __init__(self, corpus: Corpus):
        self.corpus = corpus
        self.patterns = dict()
        self.get_sequence_tuples()

    def get_sequence_tuples(self):
        for sentence in self.corpus.iter_sentences():
            print(sentence)
            print(str(sentence.annotations.pos))
            words = subgroups(items=sentence.annotations.pos.tolist(), by='word_id', starts_from=1)
            for former, latter in zip(words, words[1:]):
                former = ' '.join([' '.join([morph.form, morph.label]) for morph in former])
                latter = ' '.join([' '.join([morph.form, morph.label]) for morph in latter])

            break
