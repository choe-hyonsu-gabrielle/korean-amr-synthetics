import glob
from typing import Union
from os.path import exists
from pprint import pprint
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

    fp = open('outputs.txt', encoding='utf-8', mode='w')

    for i, snt in enumerate(corpus.filter_by(len_range=len_between, exclude=stopwords, random_state=803)):
        print('\n\n')
        print(snt.annotations.dep)
        print(snt.annotations.srl)
        print(snt.annotations.el)
        amr = AbstractMeaningRepresentation(annotations=snt.annotations)
        amr.metadata['pos'] = snt.annotations.pos.tostring()
        pprint(amr.graph.instances)
        pprint(amr.graph.relations)
        print(amr.encode())
        print()

        print(snt.annotations.dep, file=fp)
        print(snt.annotations.srl, file=fp)
        print(snt.annotations.el, file=fp)
        print(snt.annotations.cr, file=fp)
        print(snt.annotations.za, file=fp)
        print(amr.encode(), file=fp)
        print('\n\n', file=fp)

        if i > 50:
            break

    fp.close()
