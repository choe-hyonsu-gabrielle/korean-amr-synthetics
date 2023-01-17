import glob
from collections import defaultdict
from tqdm import tqdm
from synthetics.utils import load_json


class AnnotationPivot:
    def __init__(self, ref_id: str):
        self.ref_id = ref_id
        self.texts = set()
        self.layers = defaultdict(str)
        self.complete = None

    def __len__(self):
        return len(self.layers)

    def __repr__(self):
        return f'<{self.__class__.__name__} → text="{self.texts}" | layers={self.layers}>'

    def get_layers(self):
        return sorted(list(self.layers))

    def get_related_dirs(self):
        return set(self.layers.values())

    def append(self, layer: str, locator: str, text: str):
        self.layers[layer] = locator
        self.texts.add(text)


class AnnotationPivotIndexer:
    def __init__(self, layer_dirs: dict[str, str], file_extension='json'):
        self.layer_dirs = layer_dirs
        self.layer_files = {k: glob.glob(v + f'\\*.{file_extension}') for k, v in layer_dirs.items()}
        self.annotations = dict()
        self.complete_items = None
        self.complete_dirs = set()

    def __repr__(self):
        layers = tuple(self.layer_dirs.keys())
        return f'<{self.__class__.__name__} → {len(layers)} layers: {layers}>'

    def index(self):
        counts = defaultdict(int)
        layers_set = set()

        for layer, files in self.layer_files.items():
            layers_set.add(layer)
            for filename in tqdm(files, desc=f'- indexing {len(files)} files from `{layer}`({self.layer_dirs[layer]})'):
                for document_instance in load_json(filename)['document']:
                    for sentence_instance in document_instance['sentence']:
                        ref_id = sentence_instance['id']
                        text = sentence_instance['form']
                        if ref_id in self.annotations:
                            pivot = self.annotations[ref_id]
                            pivot.append(layer=layer, locator=filename, text=text)
                        else:
                            pivot = AnnotationPivot(ref_id=ref_id)
                            pivot.append(layer=layer, locator=filename, text=text)
                            self.annotations[ref_id] = pivot

        for key in self.annotations:
            layers = self.annotations[key].get_layers()
            self.annotations[key].complete = True if set(layers) == layers_set else False
            counts['-'.join(layers)] += 1

        self.complete_items = {k: v for k, v in self.annotations.items() if v.complete}

        for k, v in tqdm(self.complete_items.items(), desc=f'- aggregating file paths of `complete` files'):
            self.complete_dirs.update(v.get_related_dirs())

        print(f'- {len(self.annotations)} annotations so far: {dict(counts)}')


if __name__ == '__main__':
    search_space = 'D:\\Corpora & Language Resources\\modu-corenlp\\layers-complete\\*'
    dirs = {layer.split('\\')[-1]: layer for layer in glob.glob(search_space)}

    indexer = AnnotationPivotIndexer(layer_dirs=dirs)

    indexer.index()

    print(len(indexer.complete_dirs), indexer.complete_dirs)
    print(indexer.layer_files)
