# -*- coding: utf-8 -*-

from six import iteritems
import json
import inspect
from ..interface.message_format import CloudioMessageFormat
from ..cloudio_attribute_type import CloudioAttributeType as AttributeType
from utils import timestamp as timestamp_helpers

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

        for key, node in iteritems(endpoint.nodes):
            nodes[node.getName()] = node

        data[u'nodes'] = nodes

        message = ''
        # Encode data to json formatted byte array
        message += self._encoder.encode(data)
        return message

    def serializeNode(self, node):
        message = ''

        #message += self._encoder.startObject()
        # Encode data to json formatted byte array
        message += self._encoder.encode(node)
        #message += self._encoder.endObject()
        return message

    def serializeAttribute(self, attribute):
        data = {}
        data[u'type'] = attribute.getTypeAsString()
        data[u'constraint'] = attribute.getConstraint().toString()

        # Add timestamp only if attribute is not static
        if attribute.getConstraint() != 'static':
            timestamp = attribute.getTimestamp()
            if timestamp:
                data[u'timestamp'] = timestamp / 1000.0

        attributeValue = attribute.getValue()
        data[u'value'] = attributeValue

        message = ''
        # Encode data to json formatted byte array
        message += json.dumps(data)

        return message

    def deserializeAttribute(self, data, attribute):

        dataDict = json.loads(data)
        """:type: dict"""

        # In case there is no timestamp present, create one using
        # the current time
        if not 'timestamp' in dataDict:
            dataDict['timestamp'] = timestamp_helpers.getTimeInMilliseconds()

        if isinstance(dataDict, dict) and \
            'timestamp' in dataDict and \
            'value' in dataDict:

            timestamp = int(dataDict['timestamp'] * 1000)
            value = dataDict['value']

            if timestamp != 0 and value is not None:
                type = attribute.getType()

                if type == AttributeType.Invalid:
                    pass
                elif type == AttributeType.Boolean:
                    boolValue = False
                    if isinstance(value, str) or isinstance(value, unicode):
                        boolValue = False if value.lower() in ['0', 'false', 'falsch', 'faux', 'off'] else True
                    else:
                        boolValue = bool(value)
                    attribute.setValueFromCloud(boolValue, timestamp)
                elif type == AttributeType.Integer:
                    attribute.setValueFromCloud(int(value), timestamp)
                elif type == AttributeType.Number:
                    attribute.setValueFromCloud(float(value), timestamp)
                elif type == AttributeType.String:
                    attribute.setValueFromCloud(str(value), timestamp)
                else:
                    raise IOError('Attribute type not supported!')

class _JsonMessageEncoder(json.JSONEncoder):
    def __init__(self):
        super(_JsonMessageEncoder, self).__init__()
        pass

    def default(self, obj):
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json(self))
        elif hasattr(obj, "__dict__"):
            # Remove attributes that could cause circular references
            d = dict((key, value)
                     for key, value in inspect.getmembers(obj)
                        if not key.startswith("__") and
                           not key.startswith("_abc_") and
                           not key in ('parent', '_parent', '_externalObject') and
                           not key in ('log',) and
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