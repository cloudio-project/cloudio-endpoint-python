# -*- coding: utf-8 -*-

from .interface import uuid

class TopicUuid(uuid.Uuid):
    """Topic based Uuid (Universally Unique Identifier)

    In the case of topic based MQTT communication the topic is used directly in order to identify objects
    """

    def __init__(self, cloudIoElement=None):
        # The topic is the UUID for every object
        self._topic = None  # type: str

        if cloudIoElement:
            from cloudio_attribute import CloudioAttribute
            if isinstance(cloudIoElement, CloudioAttribute):
                try:
                    self._topic = self._getAttributeTopic(cloudIoElement)
                except:
                    self._topic = None



    ######################################################################
    # interface.Uuid implementation
    #
    def equals(self, other):
        """Returns true if the TopicUuid is equal to the given one, false otherwise.

        :param other: The TopicUuid to check equality with
        :type other: TopicUuid
        :return:
        """
        if not self.isValid() or not isinstance(other, TopicUuid) or not other.isValid():
            return False
        return True if self.topic == other.topic else False


    def isValid(self):
        return True if self.topic != None and self.topic != '' else False


    def toString(self):
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
    def _getAttributeTopic(self, cloudioAttribute):
        return self._getAttributeContainerTopic(cloudioAttribute.getParent() + u'/attributes/' +
                                                cloudioAttribute.getName())

    def _getAttributeContainerTopic(self, attributeContainer):
        return self._getObjectContainerTopic(attributeContainer.getParentObjectContainer()) + u'/objects/' + \
                                             attributeContainer.getName()

    def _getObjectContainerTopic(self, objectContainer):
        parentObjectContainer = objectContainer.getParentObjectContainer()
        if parentObjectContainer:
            return self._getObjectContainerTopic(parentObjectContainer) + u'/objects/' + objectContainer.getName()

        parentNodeContainer = objectContainer.getParentNodeContainer()
        if parentNodeContainer:
            return self._getNodeContainerTopic(parentNodeContainer) + u'/nodes/' + objectContainer.getName()

    def _getNodeContainerTopic(self, nodeContainer):
        # As the name of an node container is unique in cloud.io, we just take the name.
        return nodeContainer.getName()
