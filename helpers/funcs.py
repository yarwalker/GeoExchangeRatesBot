from functools import reduce


def deep_get(dictionary, path):
    keys = path.split('.')
    return reduce(lambda d, key: d[int(key)] if isinstance(d, list) else d.get(key) if d else None, keys, dictionary)