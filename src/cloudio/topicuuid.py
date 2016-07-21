# -*- coding: utf-8 -*-

from .interface import uuid

class TopicUuid(uuid.Uuid):
    """Topic based Uuid (Universally Unique Identifier)

    In the case of topic based MQTT communication the topic is used directly in order to identify objects
    """

    def __init__(self):
        # The topic is the UUID for every object
        self._topic = None  # type: str


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
    # API
    #

    @property
    def topic(self):
        return self._topic

    # topic.setter should only be used for testing.
    # To change the topic use one of the setTopic methods.
    @topic.setter
    def topic(self, value):
        self._topic = value
