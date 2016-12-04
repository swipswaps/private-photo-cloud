def get_first_filled_value(values):
    for value in values:
        if value:
            return value


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
