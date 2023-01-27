from pprint import pprint
from synthetics.utils import load_corpus
from synthetics.primitives.corpus import Corpus
from synthetics.primitives.amr.graph import AbstractMeaningRepresentation


if __name__ == '__main__':
    # macOS: '/Users/choe.hyonsu.gabrielle/modu-corenlp-essential/layers-complete/*/*.json'
    search_space = 'D:/Corpora & Language Resources/modu-corenlp/layers-complete/*/*.json'
    corpus: Corpus = load_corpus(data_files=search_space)

    len_between = (20, 50)
    stopwords = '\"\',“”‘’…;[]()<>'

    fp = open('outputs.txt', encoding='utf-8', mode='w')

    candidates = corpus.filter_by(len_range=len_between, exclude=stopwords, endswith='.!?', random_state=803)
    for i, snt in enumerate(candidates):
        print('\n\n')
        print(snt.annotations.dep)
        print(snt.annotations.srl)
        print(snt.annotations.el)
        print(snt.annotations.wsd)
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

        if i > 250:
            break

    fp.close()
