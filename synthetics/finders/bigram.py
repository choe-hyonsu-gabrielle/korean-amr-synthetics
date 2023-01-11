from synthetics.utils import partitions_attr
from synthetics.primitives.corpus import Corpus


class BigramPeriphrasticFinder:
    def __init__(self, corpus: Corpus):
        self.corpus = corpus
        self.patterns = dict()
        self.get_sequence_tuples()

    def get_sequence_tuples(self):
        for sentence in self.corpus.iter_sentences():
            partitioned = partitions_attr(items=sentence.annotations.pos.tolist(), by='word_id', starts_from=1)
            print(sentence)
            for p in partitioned:
                print(p)
            break
