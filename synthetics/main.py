import glob
from typing import Union
from os.path import exists
from synthetics.primitives.corpus import Corpus
from synthetics.primitives.amr import AbstractMeaningRepresentation


def load_corpus(data_files: Union[str, list[str]], reload: bool = False, pickle_file: str = 'corpus.pkl') -> Corpus:
    target_files = {layer.split('\\')[-2]: layer for layer in glob.glob(data_files)}
    if exists(pickle_file) and not reload:
        loaded = Corpus.from_pickle(filename=pickle_file)
    else:
        loaded = Corpus(files=target_files)
        loaded.to_pickle(pickle_file)
    return loaded


if __name__ == '__main__':
    # macOS: '/Users/choe.hyonsu.gabrielle/modu-corenlp-essential/layers-complete/*/*.json'

    search_space = 'D:/Corpora & Language Resources/modu-corenlp/layers-complete/*/*.json'
    corpus = load_corpus(data_files=search_space)

    len_between = (20, 50)
    stopwords = '\"\',“”‘’…;[]()<>'

    for i, snt in enumerate(corpus.filter_by(len_range=len_between, exclude=stopwords, random_state=803)):
        print('\n\n')
        print(snt.annotations.dep)
        print(snt.annotations.srl)
        print(snt.annotations.el)
        print(snt.annotations.pos.tostring())
        amr = AbstractMeaningRepresentation(annotations=snt.annotations)
        print(amr.encode())
        print()
        print(amr.graph.instances)
        print(amr.graph.relations)
        if i > 30:
            break
