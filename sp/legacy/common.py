import xml.etree.ElementTree as ET
import logging

import requests

import base64

logger = logging.getLogger('solace-provision')


def gen_creds(username, password):
    # set the credentials for SEMP REST calls
    cred = base64.b64encode(bytes("{}:{}".format(username, password), "UTF-8"))
    headers = {"Authorization": "Basic %s" % cred.decode(encoding="utf-8")}
    return cred, headers


def get_next_sequence(body):
    root = ET.fromstring(body)
    logger.debug(body)
    try:
        c = root.findall("more-cookie/rpc")[0]
        next_request = ET.tostring(c)
        next_request = "%s" % next_request.decode(encoding="utf-8")
        return next_request
    except Exception as e:
        return None


def getExecutionResult(body):
    root = ET.fromstring(body)
    try:
        c = root.findall("execute-result")[0].attrib["code"]
        return c
    except Exception as e:
        return None


# make semp request, following more-cookies by recursion as needed.
def http_semp_request(hostname, headers, request, process_callback, ignoreResponse=False, **kwargs):
    logger.debug("semp_get: {}".format(request))
    response = requests.post("{}/SEMP".format(hostname), data=request, headers=headers)
    resultCode = getExecutionResult(response.text)
    if resultCode == "fail":
        raise Exception(response.text)
    logger.debug("response: {}".format(response.text))
    if ignoreResponse:
        return
    if process_callback is not None:
        process_callback(response.text, **kwargs)
    nr = get_next_sequence(response.text)
    if nr is not None:
        logger.debug("next sequence")
        http_semp_request(hostname, headers, nr, process_callback, **kwargs)
    else:
        logger.debug("no more sequences, semp_get complete!")
        pass
    return response

