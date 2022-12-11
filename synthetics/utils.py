import json


def load_json(filename: str, encoding: str = 'utf-8'):
    """
    Simply loading json file and return the data
    :param filename: filename
    :param encoding: encoding option for open()
    :return: json data
    """
    try:
        with open(filename, encoding=encoding) as fp:
            return json.load(fp)
    except json.decoder.JSONDecodeError:
        with open(filename, encoding='utf-8-sig') as fp:
            return json.load(fp)
