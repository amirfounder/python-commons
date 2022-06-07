def merge_lists(*args):
    """
    Returns a new list
    :param args: Lists to merge
    :return: Merged list
    """
    result = []
    for arg in args:
        if isinstance(arg, list):
            result.extend(arg)
    return result
