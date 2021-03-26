# -*- coding: utf-8 -*-

import traceback
from .interface import uuid


class TopicUuid(uuid.Uuid):
    """Topic based Uuid (Universally Unique Identifier)

    In the case of topic based MQTT communication the topic is used directly in order to identify objects
    """

    def __init__(self, cloud_io_element=None):
        super(TopicUuid, self).__init__()
        # The topic is the UUID for every object
        self._topic = None  # type: str or None

        if cloud_io_element:
            from .cloudio_attribute import CloudioAttribute
            from .interface.node_container import CloudioNodeContainer
            from .interface.object_container import CloudioObjectContainer

            try:
                if isinstance(cloud_io_element, CloudioAttribute):
                    self._topic = self._get_attribute_topic(cloud_io_element)
                elif isinstance(cloud_io_element, CloudioNodeContainer):
                    self._topic = self._get_node_container_topic(cloud_io_element)
                elif isinstance(cloud_io_element, CloudioObjectContainer):
                    self._topic = self._get_object_container_topic(cloud_io_element)
            except Exception:
                traceback.print_exc()
                raise RuntimeError('Error in TopicUuid')

    ######################################################################
    # interface.Uuid implementation
    #
    def equals(self, other):
        """Returns true if the TopicUuid is equal to the given one, false otherwise.

        :param other: The TopicUuid to check equality with
        :type other: TopicUuid
        :return:
        """
        if not self.is_valid() or not isinstance(other, TopicUuid) or not other.is_valid():
            return False
        return True if self.topic == other.topic else False

    def is_valid(self):
        return True if self.topic is not None and self.topic != '' else False

    def to_string(self):
        """
        :return: Serialized TopicUuid.
        :rtype: str
        """
        return self.topic

    ######################################################################
    # Public API
    #
    @property
    def topic(self):
        return self._topic

    # topic.setter should only be used for testing.
    @topic.setter
    def topic(self, value):
        self._topic = value

    ######################################################################
    # Private methods
    #
    def _get_attribute_topic(self, cloudio_attribute):
        return self._get_attribute_container_topic(cloudio_attribute.get_parent()) + '/attributes/' + \
            cloudio_attribute.get_name()

    def _get_attribute_container_topic(self, attribute_container):
        # TODO Remove check below and put an assert for attributeContainer
        if attribute_container is None or attribute_container.get_name() is None:
            return '<no parent>' + '/objects/' + '<no name>'
        return self._get_object_container_topic(attribute_container.get_parent_object_container()) + \
            '/objects/' + attribute_container.get_name()

    def _get_object_container_topic(self, object_container):
        if not object_container:
            return '<no parent>' + '/objects/' + '<no name>'
        parentObjectContainer = object_container.get_parent_object_container()
        if parentObjectContainer:
            return self._get_object_container_topic(parentObjectContainer) + '/objects/' + object_container.get_name()

        parentNodeContainer = object_container.get_parent_node_container()
        if parentNodeContainer:
            return self._get_node_container_topic(parentNodeContainer) + '/nodes/' + object_container.get_name()

    @staticmethod
    def _get_node_container_topic(node_container):
        # As the name of an node container is unique in cloud.io, we just take the name.
        return node_container.get_name()
