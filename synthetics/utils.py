import json
import pickle
import datetime
from typing import Any, Iterable


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


def partitions_attr(items: Iterable, by: [int, str], starts_from: [int, str] = 0, scope: list = None):
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

