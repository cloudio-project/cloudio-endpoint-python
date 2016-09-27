# -*- coding: utf-8 -*-

import json
import inspect
from ..interface.message_format import CloudioMessageFormat

# Links:
# - http://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable

class JsonMessageFormat(CloudioMessageFormat):
    """Encodes messages using JSON (JavaScript Object Notation).

    All messages have to start with the identifier for this format 0x7B ('{' character).
    """
    def __init__(self):
        self._encoder = _JsonMessageEncoder()
        pass

    def serializeEndpoint(self, endpoint):
        data = {}
        nodes = {}

        for key, node in endpoint.nodes.iteritems():
            nodes[node.getName()] = node

        data[u'nodes'] = nodes

        message = bytearray()
        # Encode data to json formatted byte array
        message += self._encoder.encode(data)
        return message

    def serializeNode(self, node):
        message = bytearray()

        #message += self._encoder.startObject()
        # Encode data to json formatted byte array
        message += self._encoder.encode(node)
        #message += self._encoder.endObject()
        return message

    def serializeAttribute(self, attribute):
        data = {}
        data[u'type'] = attribute.getType().__name__
        data[u'constraint'] = attribute.getConstraint()

        # Add timestamp only if attribute is not static
        if attribute.getConstraint() != 'static':
            timestamp = attribute.getTimestamp()
            if timestamp:
                data[u'timestamp'] = timestamp / 1000.0

        attributeValue = attribute.getValue()
        data[u'value'] = attributeValue

        message = bytearray()
        # Encode data to json formatted byte array
        message += json.dumps(data)

        return message

    def deserializeAttribute(self, data, attribute):

        dataDict = json.loads(data)
        """:type: dict"""

        if isinstance(dataDict, 'dict') and \
           dataDict.has_key('timestamp') and \
           dataDict.has_key('value'):

            timestamp = int(dataDict['timestamp'] * 1000)
            value = dataDict['timestamp']

            if timestamp != 0 and value != 0:
                type = attribute.getType()
                print type



class _JsonMessageEncoder(json.JSONEncoder):
    def __init__(self):
        super(_JsonMessageEncoder, self).__init__()
        pass

    def default(self, obj):
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        elif hasattr(obj, "__dict__"):
            d = dict((key, value)
                     for key, value in inspect.getmembers(obj)
                        if not key.startswith("__") and
                           not key.startswith("_abc_") and
                           not key in ('parent', '_parent', '_externalObject') and
                           not inspect.isabstract(value) and
                           not inspect.isbuiltin(value) and
                           not inspect.isfunction(value) and
                           not inspect.isgenerator(value) and
                           not inspect.isgeneratorfunction(value) and
                           not inspect.ismethod(value) and
                           not inspect.ismethoddescriptor(value) and
                           not inspect.isroutine(value)
            )
            return self.default(d)
        return obj

    def startObject(self):
        return u'{'.encode()    # unicode to bytearray

    def endObject(self):
        return u'}'.encode()    # unicode to bytearray