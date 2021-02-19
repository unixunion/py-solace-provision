import solace_semp_client

from sp.util import getCursor


def getClient():
    config = solace_semp_client.Configuration()
    config.host = "http://localhost:8080/SEMP/v2/config"
    config.username = "admin"
    config.password = "admin"
    config.proxy = "http://localhost:5555"

    client = solace_semp_client.ApiClient(configuration=config)
    return client


def makePaginatedRequest(fetchMethod, callback, **kwargs):
    ret = fetchMethod(**kwargs)
    if callable(callback):
        callback(ret)
    cursor = getCursor(ret)
    kwargs['cursor'] = cursor
    if cursor:
        makePaginatedRequest(fetchMethod, callback, **kwargs)