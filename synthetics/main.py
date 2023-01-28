from tqdm import tqdm
from pprint import pprint
from synthetics.utils import load_corpus
from synthetics.primitives.corpus import Corpus
from synthetics.primitives.amr.graph import AbstractMeaningRepresentation


if __name__ == '__main__':
    # macOS: '/Users/choe.hyonsu.gabrielle/modu-corenlp-essential/layers-complete/*/*.json'
    search_space = 'D:/Corpora & Language Resources/modu-corenlp/layers-complete/*/*.json'
    corpus: Corpus = load_corpus(data_files=search_space)

    len_between = (20, 70)
    stopwords = '\"\',“”‘’…;[]()<>'

    fp = open('outputs.txt', encoding='utf-8', mode='w')

    counts = 0
    failed = 0
    verbose = False

    candidates = corpus.filter_by(len_range=len_between, exclude=stopwords, endswith='.!?', random_state=880830)
    # candidates = corpus.iter_sentences()
    for i, snt in enumerate(candidates):
        amr = AbstractMeaningRepresentation(annotations=snt.annotations)
        amr.metadata['pos'] = snt.annotations.pos.tostring()
        graph = amr.encode()

        if verbose:
            print('\n\n')
            print(snt.annotations.dep)
            print(snt.annotations.srl)
            print(snt.annotations.el)
            print(snt.annotations.wsd)
            pprint(amr.graph.instances)
            pprint(amr.graph.relations)
            print(graph)

        if graph:
            if verbose:
                print(snt.annotations.dep, file=fp)
                print(snt.annotations.srl, file=fp)
                print(snt.annotations.el, file=fp)
                print(snt.annotations.wsd, file=fp)
                print(snt.annotations.cr, file=fp)
                print(snt.annotations.za, file=fp)
            print(graph, file=fp, end='\n\n')

        counts += 1
        if graph is None:
            failed += 1

        if i > 1500:
            break

    fp.close()

    print(counts, failed)
