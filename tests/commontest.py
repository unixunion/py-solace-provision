from sp.util import getCursor


def makePaginatedRequest(fetchMethod, callback, **kwargs):
    ret = fetchMethod(**kwargs)
    if callable(callback):
        callback(ret)
    cursor = getCursor(ret)
    kwargs['cursor'] = cursor
    if cursor:
        makePaginatedRequest(fetchMethod, callback, **kwargs)
