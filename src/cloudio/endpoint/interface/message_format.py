# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

from cloudio.endpoint.attribute import CloudioAttribute
from cloudio.endpoint.node import CloudioNode


class CloudioMessageFormat(object):
    """
    The CloudioMessageFormat interface declares the methods that are used by the {@link CloudioEndpoint}
    implementation in order to encode and decode attribute changes into MQTT messages.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def serialize_endpoint(self, endpoint):
        """A CloudioMessageFormat implementation should return the encoded payload of the serialization of the
           given endpoint.

        :param endpoint: Endpoint to serialize.
        :type endpoint: CloudioEndpoint
        :return: Raw data representation of the endpoint.
        :rtype: Json or Cbor serialized
        """
        pass

    @abstractmethod
    def serialize_node(self, node):
        """A CloudioMessageFormat implementation should return the encoded payload of the serialization of the
           given node.

        :param node: Node to serialize.
        :type node: CloudioNode
        :return: Raw data representation of the node.
        :rtype: Json or Cbor serialized
        """
        pass

    @abstractmethod
    def serialize_attribute(self, attribute):
        """A CloudioMessageFormat implementation should return the encoded payload of the serialization of the
           given attribute.

        :param attribute: Attribute to serialize.
        :type attribute: CloudioAttribute
        :return: Raw data representation of the attribute.
        :rtype: Json or Cbor serialized
        """
        pass

    @abstractmethod
    def deserialize_attribute(self, data, attribute):
        """A CloudioMessageFormat implementation should parse the data payload and update the given attribute
           according to the data.

        :param data: Data received in the MQTT message.
        :type data: Json or Cbor serialized
        :param attribute: Attribute to update using the raw message data.
        :type attribute: CloudioAttribute
        """
        pass

    @abstractmethod
    def serialize_transaction(self, transaction):
        """A CloudioMessageFormat implementation should return the encoded payload of the serialization of the
                   given transaction.

                :param transaction: Node to serialize.
                :type transaction: Transaction
                :return: Raw data representation of the node.
                :rtype: Json or Cbor serialized
                """
        pass

    @abstractmethod
    def serialize_delayed(self, persistence):
        pass
