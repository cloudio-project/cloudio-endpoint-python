import cbor
import json

from cloudio.endpoint.interface import CloudioMessageFormat
from cloudio.endpoint.message_format.json_format import JsonMessageFormat


class CborMessageFormat(CloudioMessageFormat):
    def __init__(self):
        self._jsonFormat = JsonMessageFormat()
        pass

    def serialize_endpoint(self, endpoint):
        data = bytearray(cbor.dumps(self._jsonFormat.serialize_endpoint(endpoint)))

        # delete the first characters produce by cbor library until "{"
        while data[0] != 123:
            del data[0]

        return data

    def serialize_node(self, node):
        data = bytearray(cbor.dumps(self._jsonFormat.serialize_node(node)))

        # delete the first characters produce by cbor library until "{"
        while data[0] != 123:
            del data[0]

        return data

    def serialize_attribute(self, attribute):
        data = bytearray(cbor.dumps(self._jsonFormat.serialize_attribute(attribute)))

        #delete the first characters produce by cbor library until "{"
        while data[0] != 123:
            del data[0]

        return data

    def deserialize_attribute(self, data, attribute):
        a = cbor.loads(data)
        self._jsonFormat.deserialize_attribute(json.dumps(a), attribute)