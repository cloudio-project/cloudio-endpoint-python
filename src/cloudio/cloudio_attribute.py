# -*- coding: utf-8 -*-

import logging
from .topicuuid import TopicUuid
from cloudio.interface.unique_identifiable import UniqueIdentifiable
from cloudio.interface.attribute_container import CloudioAttributeContainer
from cloudio.interface.attribute_listener import AttributeListener
from cloudio.exception.cloudio_modification_exception import CloudioModificationException
from cloudio.exception.invalid_cloudio_attribute_exception import InvalidCloudioAttributeException
from cloudio.cloudio_attribute_type import CloudioAttributeType as AttributeType
from cloudio.cloudio_attribute_constraint import CloudioAttributeConstraint as AttributeConstraint
import utils.py_version_compatibility as types
import utils.timestamp as TimeStampProvider

class CloudioAttribute(UniqueIdentifiable):
    """The leaf information in the cloud.io data model
    """

    log = logging.getLogger(__name__)

    def __init__(self):
        self._name = None           # type: str
        self._parent = None
        self._topicUuid = None      # type: TopicUuid
        self._constraint = None
        self._type = None           # type: AttributeType
        self._timestamp = None
        self._value = None          # type: dynamic
        self._listeners = None      # type: list[AttributeListener]

    def addListener(self, listener):
        """Adds the given listener to the list of listeners that will get informed about a change of the attribute.

        :param listener: Reference to the object implementing the AttributeListener interface to add.
        :type listener: AttributeListener
        """
        if listener is not None:
            # Lazy initialization of the listener list
            if self._listeners is None:
                self._listeners = []

            # Finally add the listener
            self._listeners.append(listener)

    def removeListener(self, listener):
        """Removes the given listener from the list of listeners.

        :param listener: Reference to the object implementing the AttributeListener interface to remove.
        :type listener: AttributeListener
        """
        if listener is not None and self._listeners is not None:
            self._listeners.remove(listener)

    ######################################################################
    # UniqueIdentifiable implementation
    #
    def getUuid(self):
        if not self._topicUuid:
            self._topicUuid = TopicUuid(self)

        return self._topicUuid

    def setValue(self, value, timestamp=None):
        if not timestamp:
            timestamp = TimeStampProvider.getTimeInMilliseconds()

        # TODO Check constraint.

        # Update value
        self._timestamp = timestamp
        self._setValueWithTypeCheck(value)

        # Send change to cloud.
        if self.getParent():
            self.getParent().attributeHasChangedByEndpoint(self)

        # TODO Inform all registered listeners.

    def setValueFromCloud(self, value, timestamp):
        """Updates the value from the cloud.

         Note that this method should not be used by endpoints, as it guarantees
         that only attributes with semantics compatible with cloud updates can be updated.

        :param value: New value to set from cloud.
        :param timestamp: Timestamp of the value from the cloud.
        :return: True if the value was updated, false if not.
        """

        # TODO: Check if the cloud can change the attribute.
        # self.constraint.cloudWillChange()

        # Check if the value from the cloud is older than the actual one and do nothing if that is the case.
        if self._timestamp is not None and self._timestamp >= timestamp:
            print('Warning: Ignoring new value from cloud.iO. Not valid timestamp!')
            return False

        # Update the value
        self._timestamp = timestamp
        self._setValueWithTypeCheck(value)

        # Notify the cloud.
        if self._parent is not None:
            self._parent.attributeHasChangedByCloud(self)

        # Notify all listeners.
        if self._listeners is not None:
            for listener in self._listeners:
                # noinspection unchecked
                listener.attributeHasChanged(self)
        else:
            self.log.warning('No listeners connected to attribute \"' + self.getName() + '\"!')

        return True

    def _setValueWithTypeCheck(self, value):
        """Assigns a new value and checks the rvalue type.
        """
        if self._type == AttributeType.Boolean:
            self._value = bool(value)
        elif self._type == AttributeType.Integer:
            self._value = int(value)
        elif self._type == AttributeType.Number:
            self._value = float(value)
        elif self._type == AttributeType.String:
            assert isinstance(value, str)
            self._value = value
        else:
            self.log.warning('Need to assign value which has unsupported type!')
            self._value = value

    def getType(self):
        """Returns the actual type of the attribute."""
        if self._type is not None:
            return self._type.type
        else:
            self.log.warning('Deprecated call to getType()!')
            return AttributeType.fromRawType(type(self._value))


    def getTypeAsString(self):
        """Returns the actual type of the attribute as a string."""
        if self._type is not None:
            return self._type.toString()
        else:
            self.log.warning('Deprecated call to getTypeAsString()!')
            AttributeType.fromRawTypeToString(type(self._value))

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

    def setType(self, theType):
        """Sets the type of the attribute.

        Note that the type of an attribute is not allowed to change over time, so if
        the attribute already has a type, the method fails with an runtime exception.

        :param theType Python type like bool, int, float and str
        :type [bool, int, float, str]
        """
        if self._value:
            raise CloudioModificationException(u'The Attribute has already a type (Changing the type is not allowed)!')

        if theType in (types.BooleanType, types.IntType, types.LongType, types.FloatType, types.StringType):
            self._value = theType()

            # Set cloudio attribute type accordingly
            if theType == types.BooleanType:
                self._type = AttributeType(AttributeType.Boolean)
            elif theType in (types.IntType, types.LongType):
                self._type = AttributeType(AttributeType.Integer)
            elif theType == types.FloatType:
                self._type = AttributeType(AttributeType.Number)
            elif theType == types.StringType:
                self._type = AttributeType(AttributeType.String)
            else:
                self._type = AttributeType(AttributeType.Invalid)
        else:
            raise InvalidCloudioAttributeException(theType)

    ######################################################################
    # Public API
    #
    def getTimestamp(self):
        return self._timestamp

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

        self._setValueWithTypeCheck(value)

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
        #assert isinstance(parent, CloudioAttributeContainer), u'Wrong type for parent attribute!'
        self._parent = parent

    def getConstraint(self):
        return self._constraint

    def setConstraint(self, constraint):
        """

        :param constraint:
        :type constraint: CloudioAttributeConstraint
        :return:
        """
        assert isinstance(constraint, AttributeConstraint), u'Wrong type'

        if self._constraint:
            raise CloudioModificationException('The Attribute has already a constraint ' +
                                               '(Changing constraints is not allowed)!')
        # Set the constraint
        self._constraint = constraint

    def to_json(self, encoder):
        """Pick out the attributes we want to store / publish.
        """
        attrDict = {}

        # Name should not be added for @online message
        #attrDict['name'] = self._name

        # Get the type of the value and convert it to cloud.io attribute type
        attrDict['type'] = AttributeType.fromRawTypeToString(self._value)
        attrDict['value'] = self._value
        #attrDict['timestamp'] = self._timestamp
        attrDict['constraint'] = self._constraint

        return encoder.default(attrDict)



