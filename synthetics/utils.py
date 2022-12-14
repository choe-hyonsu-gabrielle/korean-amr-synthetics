import json


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
