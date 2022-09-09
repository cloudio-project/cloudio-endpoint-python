import cbor

from cloudio.endpoint.interface import CloudioMessageFormat
from cloudio.endpoint.message_format.generic_format import GenericMessageFormat


class CborMessageFormat(CloudioMessageFormat):
    """Encodes messages using CBOR.

    All messages have to start with the identifier for this format 0b101.
    """

    def __init__(self):
        self._genericFormat = GenericMessageFormat()
        pass

    def serialize_endpoint(self, endpoint):
        return cbor.dumps(self._genericFormat.serialize_endpoint(endpoint))

    def serialize_node(self, node):
        return cbor.dumps(self._genericFormat.serialize_node(node))

    def serialize_attribute(self, attribute):
        return cbor.dumps(self._genericFormat.serialize_attribute(attribute))

    def deserialize_attribute(self, data, attribute):
        self._genericFormat.deserialize_attribute(cbor.loads(data), attribute)

    def serialize_transaction(self, transaction):
        return cbor.dumps(self._genericFormat.serialize_transaction(transaction))

    def serialize_delayed(self, persistence):
        return cbor.dumps(self._genericFormat.serialize_delayed(persistence))

    def dumps(self, data):
        return cbor.dumps(data)

    def loads(self, data):
        return cbor.loads(data)
