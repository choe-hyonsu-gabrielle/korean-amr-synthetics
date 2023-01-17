import json
from collections import defaultdict, Counter
from synthetics.utils import load_pickle
from synthetics.primitives.corpus import Corpus, NERItem
from synthetics.rules.named_entity import NAMED_ENTITIES

if __name__ == '__main__':
    corpus: Corpus = load_pickle('../corpus.pkl')

    ne_counts = defaultdict(list)
    for snt in corpus.iter_sentences():
        for ne in snt.annotations.ner.tolist():
            ne: NERItem
            ne_counts[ne.label].append(ne.form)

    for ne_class in ne_counts:
        ne_counts[ne_class] = Counter(ne_counts[ne_class]).most_common()

    print(set(NAMED_ENTITIES).difference(set(ne_counts)))

    catalog = dict()
    for key in NAMED_ENTITIES:
        catalog[key] = dict(types=len(ne_counts.get(key, [])))
        for span, freq in ne_counts.get(key, []):
            catalog[key][span] = freq

    with open('named-entity.json', encoding='utf-8', mode='w') as fp:
        json.dump(catalog, fp, ensure_ascii=False, indent=4)