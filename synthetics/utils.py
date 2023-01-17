import os
import json
import glob
import pickle
import datetime
from os.path import exists
from typing import Any, Union, Iterable


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


def get_absolute_root_path(root_name='synthetics', suffix='\\'):
    """ get absolute root path
    :param: root_name: dir name for project root.
    :param: suffix: path delimiter
    :return: If the call location is "C:/Users/.../Projects/synthetics/dir1/demo",
             then return will be "C:/Users/.../Projects/synthetics"
    """
    current_location = os.getcwd()
    cut = current_location.rfind(root_name)
    return ''.join([current_location[:cut], root_name]) + suffix


def load_corpus(data_files: Union[str, list[str]], reload: bool = False, pickle_file: str = 'corpus.pkl'):
    # the `from ... import ...` statement below is located here to prevent circular import. do not relocate it.
    from synthetics.primitives.corpus import Corpus
    target_files = {layer.split('\\')[-2]: layer for layer in glob.glob(data_files)}
    if exists(pickle_file) and not reload:
        loaded = Corpus.from_pickle(filename=pickle_file)
    else:
        loaded = Corpus(files=target_files)
        loaded.to_pickle(pickle_file)
    return loaded


def save_pickle(filename: str, instance: Any):
    with open(filename, 'wb') as fp:
        pickle.dump(instance, fp, pickle.HIGHEST_PROTOCOL)


def load_pickle(filename: str):
    with open(filename, 'rb') as fp:
        return pickle.load(fp)


def timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


def ngrams(items: list, n: int):
    assert 0 < n, 'incorrect `n` value.'
    results = []
    for start in range(len(items) - n + 1):
        end = start + n
        n_gram = items[start:end]
        if n_gram:
            results.append(n_gram)
    return results


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
