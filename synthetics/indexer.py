import glob
import random
from collections import defaultdict
from tqdm import tqdm
from synthetics.utils import load_json


class AnnotationPivot:
    def __init__(self, ref_id):
        self.ref_id = ref_id
        self.texts = defaultdict(str)
        self.layers = defaultdict(str)
        self.complete = None

    def __len__(self):
        return len(self.layers)

    def __repr__(self):
        return f'<{self.__class__.__name__} → text="{self.texts}" | layers={self.layers}>'

    def get_layers(self):
        return sorted(list(self.layers))

    def append(self, layer: str, locator: str, text: str):
        self.texts[layer] = text
        self.layers[layer] = locator


class AnnotationPivotIndexer:
    def __init__(self, layer_dirs: dict[str, str], file_extension='json'):
        self.layer_dirs = layer_dirs
        self.layer_files = {k: glob.glob(v + f'\\*.{file_extension}') for k, v in layer_dirs.items()}
        self.annotations = dict()

    def __repr__(self):
        layers = tuple(self.layer_dirs.keys())
        return f'<{self.__class__.__name__} → {len(layers)} layers: {layers}>'

    @property
    def complete_items(self):
        return list({k: v for k, v in self.annotations.items() if v.complete}.items())

    def index(self):
        counts = defaultdict(int)
        processed_layers = []

        for layer, files in self.layer_files.items():
            processed_layers.append(layer)
            for filename in tqdm(files, desc=f'- indexing {len(files)} files from `{layer}`({self.layer_dirs[layer]})'):
                data = load_json(filename)
                for document_instance in data['document']:
                    for sentence_instance in document_instance['sentence']:
                        ref_id = sentence_instance['id']
                        text = sentence_instance['form']
                        if ref_id in self.annotations:
                            pivot = self.annotations[ref_id]
                            pivot.append(layer=layer, locator=filename, text=text)
                        else:
                            pivot = AnnotationPivot(ref_id)
                            pivot.append(layer=layer, locator=filename, text=text)
                            self.annotations[ref_id] = pivot

        for key in self.annotations:
            layers = self.annotations[key].get_layers()
            self.annotations[key].complete = True if set(layers) == set(processed_layers) else False
            counts['-'.join(layers)] += 1

        print(f'- {len(self.annotations)} annotations so far: {dict(counts)}')


if __name__ == '__main__':
    search_space = 'D:\\Corpora & Language Resources\\modu-corenlp\\layers\\*'
    dirs = {layer.split('\\')[-1]: layer for layer in glob.glob(search_space)}

    indexer = AnnotationPivotIndexer(layer_dirs=dirs)
    print(indexer)

    indexer.index()

    for idx, anno in random.sample(indexer.complete_items, k=10):
        print(anno)


