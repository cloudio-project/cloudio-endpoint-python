# -*- coding: utf-8 -*-

import types
from topicuuid import TopicUuid
from interface.unique_identifiable import UniqueIdentifiable
from exception.cloudio_modification_exception import CloudioModificationException
from exception.invalid_cloudio_attribute_exception import InvalidCloudioAttributeException
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

    ######################################################################
    # UniqueIdentifiable implementation
    #
    def getUuid(self):
        if not self._topicUuid:
            self._topicUuid = TopicUuid(self)

        return self._topicUuid

    ######################################################################
    # Named item implementation
    #
    def getName(self):
        return self._name

    def setName(self, name):
        """
        :type name: str
        """
        # If the attribute already has a name (we are renaming the attribute) then fail with a runtime exception.
        if self._name != None:
            raise CloudioModificationException('The Attribute has already a name (Renaming attributes is forbidden)!')

        assert name and name != '', 'Name not valid!'
        self._name = name

    def getValue(self):
        """Returns the current value of the attribute.
        :return: Attributes current value.
        """
        return self._value

    def getType(self):
        """Returns the actual type of the attribute."""
        return type(self._value)

    def setType(self, theType):
        """Sets the type of the attribute.

        Note that the type of an attribute is not allowed to change over time, so if
        the attribute already has a type, the method fails with an runtime exception.
        """
        if self._value:
            raise CloudioModificationException(u'The Attribute has already a type (Changing the type is not allowed)!')

        if theType in (types.BooleanType, types.IntType, types.LongType, types.FloatType, types.StringType):
            self._value = theType()
        else:
            raise InvalidCloudioAttributeException(theType)

    ######################################################################
    # Public API
    #
    def setStaticValue(self, value):
        """Initializes the static value

        This can be only done using static attributes (@StaticAttribute or @Static).
        The value of a static attribute can be changed as often as wanted, the only constraint is that the node
        containing the static attribute has not been registered within the endpoint.

        :param value: The initial value to set
        :return:
        """
        # TODO Check constraint
        #self._constraint.endpointWillChangeStatic()

        self._value = value

    def getParent(self):
        return self._parent

    def setParent(self, parent):
        """Sets the parent of the attribute. Note that attributes can not be moved, so this method throws a runtime
           exception if someone tries to move the attribute to a new parent.
        """
        # If the attribute already has a parent (we are moving the attribute) then fail with a runtime exception.
        if self._parent:
            raise CloudioModificationException('The parent of an Attribute can never be changed ' +
                                               '(Attributes can not be moved)!')

    def getConstraint(self):
        return self._constraint

    def setConstraint(self, constaint):
        """

        :param constaint:
        :type constaint: str (for the moment)
        :return:
        """
        # TODO Change constraint type to CloudioAttributeConstraint
        if self._constraint:
            raise CloudioModificationException('The Attribute has already a constraint ' +
                                               '(Changing constraints is not allowed)!')
        # Set the constraint
        self._constraint = constaint