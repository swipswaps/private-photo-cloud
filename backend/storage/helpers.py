import base64

import binascii


def get_filled_value(values):
    # works better on long sequence: return next(filter(None, values), None)
    # loop works best on short sequence
    for value in values:
        if value:
            return value


def get_keys_filled_value(data, keys):
    return get_filled_value(data.get(k) for k in keys)


def get_re_keys_filled_value(data, key_re):
    return get_filled_value(v for k, v in data.items() if key_re.search(k))


def resolve_dict(path, data):
    """
    Resolve dict item by path (split by ':').

    Example:
        resolve_dict('tags:created_at', {'tags': {'created_at': True}})

    Analogue:
        Variable('tags.created_at').resolve({'tags': {'created_at': True}})
    """
    keys = path.split(':')
    for key in keys:
        try:
            data = data[key]
        except KeyError:
            return None
    return data


def map_dict(data, mappings):
    return {mappings.get(k, k): v for k, v in data.items()}


def base85_to_hex(base85_text):
    return base64.b85decode(base85_text).hex()


def hex_to_base85(hex_text):
    return base64.b85encode(binascii.unhexlify(hex_text))
