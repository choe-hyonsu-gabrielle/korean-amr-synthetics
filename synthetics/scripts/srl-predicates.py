from collections import defaultdict
from synthetics.utils import load_pickle
from synthetics.primitives.corpus import Corpus, SRLItem

if __name__ == '__main__':
    corpus: Corpus = load_pickle('../corpus.pkl')
    pred_counts = defaultdict(int)

    for snt in corpus.iter_sentences():
        for srl in snt.annotations.srl.tolist():
            srl: SRLItem
            pred_counts[srl.predicate.lemma] += 1

    pred_counts = sorted(pred_counts.items(), key=lambda x: x[1], reverse=True)
    for pred, freq in pred_counts:
        print(pred, freq)

    with open('srl-predicates.tsv', encoding='utf-8', mode='w') as fp:
        fp.write('pred\tcount\n')
        for pred, freq in pred_counts:
            fp.write(f'{pred}\t{freq}\n')
