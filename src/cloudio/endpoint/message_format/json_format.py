# -*- coding: utf-8 -*-

import inspect
import json

from cloudio.common.utils import timestamp_helpers as timestamp_helpers
from cloudio.endpoint.attribute.type import CloudioAttributeType as AttributeType
from cloudio.endpoint.interface.message_format import CloudioMessageFormat


# Links:
# - http://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable

class JsonMessageFormat(CloudioMessageFormat):
    """Encodes messages using JSON (JavaScript Object Notation).

    All messages have to start with the identifier for this format 0x7B ('{' character).
    """

    def __init__(self):
        self._encoder = _JsonMessageEncoder()
        pass

    def serialize_endpoint(self, endpoint):
        data = {}
        nodes = {}

        for key, node in endpoint.nodes.items():
            nodes[node.get_name()] = node

        data['nodes'] = nodes

        #TODO clean endpoint serialization
        data['version'] = "v0.2"
        data['messageFormatVersion'] = 2
        data['supportedFormats'] = ["JSON"]

        message = ''
        # Encode data to json formatted byte array
        message += self._encoder.encode(data)
        return message

    def serialize_node(self, node):
        message = ''

        # message += self._encoder.startObject()
        # Encode data to json formatted byte array
        message += self._encoder.encode(node)
        # message += self._encoder.endObject()
        return message

    def serialize_attribute(self, attribute):
        data = {}
        data['type'] = attribute.get_type_as_string()
        data['constraint'] = attribute.get_constraint().to_string()

        # Add timestamp only if attribute is not static
        if attribute.get_constraint() != 'static':
            timestamp = attribute.get_timestamp()
            if timestamp:
                data['timestamp'] = timestamp / 1000.0

        attribute_value = attribute.get_value()
        data['value'] = attribute_value

        message = ''
        # Encode data to json formatted byte array
        message += json.dumps(data)

        return message

    def deserialize_attribute(self, data, attribute):

        data_dict = json.loads(data)
        """:type: dict"""

        # In case there is no timestamp present, create one using
        # the current time
        if not 'timestamp' in data_dict:
            data_dict['timestamp'] = timestamp_helpers.get_time_in_milliseconds()

        if isinstance(data_dict, dict) and \
                'timestamp' in data_dict and \
                'value' in data_dict:

            timestamp = int(data_dict['timestamp'] * 1000)
            value = data_dict['value']

            if timestamp != 0 and value is not None:
                type = attribute.get_type()

                if type == AttributeType.Invalid:
                    pass
                elif type == AttributeType.Boolean:
                    bool_value = False
                    if isinstance(value, str):
                        bool_value = False if value.lower() in ['0', 'false', 'falsch', 'faux', 'off'] else True
                    else:
                        bool_value = bool(value)
                    attribute.set_value_from_cloud(bool_value, timestamp)
                elif type == AttributeType.Integer:
                    attribute.set_value_from_cloud(int(value), timestamp)
                elif type == AttributeType.Number:
                    attribute.set_value_from_cloud(float(value), timestamp)
                elif type == AttributeType.String:
                    attribute.set_value_from_cloud(str(value), timestamp)
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
        return '{'.encode()  # unicode to bytearray

    def endObject(self):
        return '}'.encode()  # unicode to bytearray
