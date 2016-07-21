# -*- coding: utf-8 -*-

from topicuuid import TopicUuid
from interface.unique_identifiable import UniqueIdentifiable
from exception.cloudio_modification_exception import CloudioModificationException
import utils.timestamp as TimeStampProvider

class CloudioAttribute():
    """The leaf information in the cloud.io data model
    """
    def __init__(self):
        self._internal = _InternalAttribute()

    def getValue(self):
        return self._internal._value

    def setValue(self, value, timestamp=None):
        if not timestamp:
            timestamp = TimeStampProvider.getTimeInMilliseconds()

        # TODO Check constraint.

        # Update value
        self._internal._timestamp = timestamp
        self._internal._value = value

        # TODO Send change to cloud.

        # TODO Inform all registered listeners.

    def getParent(self):
        return self._internal._parent

class _InternalAttribute(UniqueIdentifiable):
    def __init__(self):
        # TODO Explain each of the attributes
        self._name = None       # type: str
        self._parent = None
        self._topicUuid = None  # type: TopicUuid
        self._constraint = None
        self._rawType = None
        self._timestamp = None
        self._value = None      # type: dynamic
        self._listeners = None

    #
    # UniqueIdentifiable implementation
    #
    def getUuid(self):
        if not self._topicUuid:
            self._topicUuid = TopicUuid(self)

        return self._topicUuid

    #
    # Named item implementation
    #
    def setName(self, name):
        """
        :type name: str
        """
        # If the attribute already has a name (we are renaming the attribute) then fail with a runtime exception.
        if self._name != None:
            raise CloudioModificationException('The Attribute has already a name (Renaming attributes is forbidden)!')

        assert name and name != '', 'Name not valid!'
        self._name = name

    def getName(self):
        return self._name

    def getValue(self):
        """Returns the current value of the attribute.
        :return: Attributes current value.
        """
        return self._value

    def getType(self):
        """Returns the actual type of the attribute."""
        return type(self._value)
