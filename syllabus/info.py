def parent_name(name):
    parts = name.split('::')
    if len(parts) < 2:
        return None
    return '::'.join(parts[:-1])


def is_child(name):
    return parent_name(name) is not None


def hierarchy_names(name):
    parts = name.split('::')
    return ['::'.join(parts[:index + 1]) for index in range(len(parts))]
