import json

from cloudio.endpoint.interface import CloudioMessageFormat
from cloudio.endpoint.message_format.generic_format import GenericMessageFormat


class JsonMessageFormat(CloudioMessageFormat):
    """Encodes messages using JSON (JavaScript Object Notation).

    All messages have to start with the identifier for this format 0x7B ('{' character).
    """
    def __init__(self):
        self._genericFormat = GenericMessageFormat()
        pass
    def serialize_endpoint(self, endpoint):
        message = ''
        # Encode data to json formatted byte array
        message += json.dumps(self._genericFormat.serialize_endpoint(endpoint))
        return message

    def serialize_node(self, node):
        message = ''
        # Encode data to json formatted byte array
        message += json.dumps(self._genericFormat.serialize_node(node))
        return message

    def serialize_attribute(self, attribute):
        message = ''
        # Encode data to json formatted byte array
        message += json.dumps(self._genericFormat.serialize_attribute(attribute))
        return message

    def deserialize_attribute(self, data, attribute):
        self._genericFormat.deserialize_attribute(json.loads(data), attribute)