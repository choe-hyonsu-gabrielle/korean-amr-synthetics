import json
import glob
import pickle
import datetime
from typing import Any, Iterable
from collections import defaultdict
from tqdm import tqdm


def load_json(filepath: str, encoding: str = 'utf-8'):
    """
    Simply loading json file and return the data
    :param filepath: filename or path
    :param encoding: encoding option for open()
    :return: json data
    """
    try:
        with open(filepath, encoding=encoding) as fp:
            return json.load(fp)
    except json.decoder.JSONDecodeError:
        with open(filepath, encoding='utf-8-sig') as fp:
            return json.load(fp)


def save_pickle(filename: str, instance: Any):
    with open(filename, 'wb') as fp:
        pickle.dump(instance, fp, pickle.HIGHEST_PROTOCOL)


def load_pickle(filename: str):
    with open(filename, 'rb') as fp:
        return pickle.load(fp)


def timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


def subgroups(items: Iterable, by: [int, str], starts_from: [int, str] = 0, scope: list = None):
    """
    split single list to partitioned list by attribute of elements
    :param items: a single iterable object
    :param by: if you want to split the list by particular attribute (ex. key of dict) then pass str,
               or you can pass int value (ex. specific index of every individual)
    :param starts_from: initial value to be compared with `by`
    :param scope: if you pass a sequence as a `scope`, then it will return only expected outputs
                  corresponding to the attributes or index of individuals in the range of scope.
                  (ex. ['key1', 'key2', ...] or [2, 3, 4, ...])
    :return: a list of lists
    """
    result = list()
    buffer = list()
    current_state = starts_from
    if scope and starts_from not in scope:
        raise ValueError(f'Wrong arguments - starts_from: {starts_from} ({type(starts_from)}), scope: {scope}')
    for element in items:
        if isinstance(by, str) and isinstance(element, dict):
            criterion = element[by]
        elif isinstance(by, str) and isinstance(element, tuple):  # namedtuple
            criterion = getattr(element, by)
        elif isinstance(by, int) and isinstance(element, (list, tuple)):
            criterion = element[by]
        elif isinstance(by, str):
            criterion = element.__getattribute__(by)
        else:
            raise ValueError(f'Wrong arguments - item: {element} ({type(element)}), by: {by} ({type(by)})')
        if scope and criterion not in scope:
            continue
        if current_state == criterion:
            buffer.append(element)
        else:
            current_state = criterion
            result.append(buffer)
            buffer = list()
            buffer.append(element)
    result.append(buffer)  # last pang
    return result


def partitions_size(items: [list, tuple, set], n: int):
    """
    split the list to groups of elements, which has same size
    :param items: iterable
                  (ex. assume that items = [1, 2, 3, 4, 5, 6, ...])
    :param n: size of subgroups
              (ex. if n = 3, then return will be [[1, 2, 3] [4, 5, 6], ...])
    :return: a list of lists
    """
    return [items[i * n:(i + 1) * n] for i in range((len(items) + n - 1) // n)]


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

