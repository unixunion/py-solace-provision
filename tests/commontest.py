from sp.util import get_cursor


def makePaginatedRequest(fetchMethod, callback, **kwargs):
    ret = fetchMethod(**kwargs)
    if callable(callback):
        callback(ret)
    cursor = get_cursor(ret)
    kwargs['cursor'] = cursor
    if cursor:
        makePaginatedRequest(fetchMethod, callback, **kwargs)
