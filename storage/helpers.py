def get_first_filled_value(values):
    # loop works best on short sequence
    for value in values:
        if value:
            return value
    # works better on long sequence
    # return next(filter(None, values), None)


def get_first_filled_key(data, keys):
    return get_first_filled_value(data.get(k) for k in keys)


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
