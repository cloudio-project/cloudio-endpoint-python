# -*- coding: utf-8 -*-

import logging
import cloudio.common.utils.timestamp as TimeStampProvider
from cloudio.endpoint.topicuuid import TopicUuid
from cloudio.endpoint.interface.unique_identifiable import UniqueIdentifiable
from cloudio.endpoint.interface.attribute_listener import AttributeListener
from cloudio.endpoint.exception.cloudio_modification_exception import CloudioModificationException
from cloudio.endpoint.exception.invalid_cloudio_attribute_exception import InvalidCloudioAttributeException
from cloudio.endpoint.attribute.type import CloudioAttributeType as AttributeType
from cloudio.endpoint.attribute.constraint import CloudioAttributeConstraint as AttributeConstraint


class CloudioAttribute(UniqueIdentifiable):
    """The leaf information in the cloud.io data model
    """

    log = logging.getLogger(__name__)

    def __init__(self):
        self._name = None           # type: str or None
        self._parent = None
        self._topicUuid = None      # type: TopicUuid or None
        self._constraint = None
        self._type = None           # type: AttributeType or None
        self._timestamp = None
        self._value = None          # type: bool or int or float or str or None
        self._listeners = None      # type: list[AttributeListener] or None

    def add_listener(self, listener):
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

    def remove_listener(self, listener):
        """Removes the given listener from the list of listeners.

        :param listener: Reference to the object implementing the AttributeListener interface to remove.
        :type listener: AttributeListener
        """
        if listener is not None and self._listeners is not None:
            self._listeners.remove(listener)

    ######################################################################
    # UniqueIdentifiable implementation
    #
    def get_uuid(self):
        if not self._topicUuid:
            self._topicUuid = TopicUuid(self)

        return self._topicUuid

    def set_value(self, value, timestamp=None):
        if not timestamp:
            timestamp = TimeStampProvider.getTimeInMilliseconds()

        # TODO Check constraint.

        # Update value
        self._timestamp = timestamp
        self._set_value_with_type_check(value)

        # Send change to cloud.
        if self.get_parent():
            self.get_parent().attribute_has_changed_by_endpoint(self)

        # TODO Inform all registered listeners.

    def set_value_from_cloud(self, value, timestamp):
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
        self._set_value_with_type_check(value)

        # Notify the cloud.
        if self._parent is not None:
            self._parent.attribute_has_changed_by_cloud(self)

        # Notify all listeners.
        if self._listeners:
            for listener in self._listeners:
                # noinspection unchecked
                listener.attribute_has_changed(self)
        else:
            self.log.warning('No listeners connected to attribute \"' + self.get_name() + '\"!')

        return True

    def _set_value_with_type_check(self, value):
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
            self.set_type(type(value))  # Try to set the type
            self._value = value

    def get_type(self):
        """Returns the actual type of the attribute."""
        if self._type is not None:
            return self._type.type
        else:
            self.log.warning('Deprecated call to get_type()!')
            return AttributeType.from_raw_type(type(self._value))

    def get_type_as_string(self):
        """Returns the actual type of the attribute as a string."""
        if self._type is not None:
            return self._type.to_string()
        else:
            self.log.warning('Deprecated call to get_type_as_string()!')
            AttributeType.from_raw_type_to_string(type(self._value))

    ######################################################################
    # Named item implementation
    #
    def get_name(self):
        return self._name if self._name else 'unknown'

    def set_name(self, name):
        """
        :type name: str
        """
        # If the attribute already has a name (we are renaming the attribute) then fail with a runtime exception.
        if self._name is not None:
            raise CloudioModificationException('The Attribute has already a name (Renaming attributes is forbidden)!')

        assert name and name != '', 'Name not valid!'
        self._name = name

    def get_value(self):
        """Returns the current value of the attribute.
        :return: Attributes current value.
        """
        return self._value

    def set_type(self, the_type: [bool, int, float, str]):
        """Sets the type of the attribute.

        Note that the type of an attribute is not allowed to change over time, so if
        the attribute already has a type, the method fails with an runtime exception.

        :param the_type Python type like bool, int, float and str
        :type [bool, int, float, str]
        """
        if self._value:
            raise CloudioModificationException('The Attribute has already a type (Changing the type is not allowed)!')

        if the_type in (bool, int, float, bytes, str):
            self._value = the_type()

            # Init to invalid
            self._type = AttributeType(AttributeType.Invalid)

            # Set cloudio attribute type accordingly
            if the_type in (bool, ):
                self._type = AttributeType(AttributeType.Boolean)
            elif the_type in (int, ):
                self._type = AttributeType(AttributeType.Integer)
            elif the_type in (float, ):
                self._type = AttributeType(AttributeType.Number)
            else:
                assert the_type in (bytes, str), 'Seems we got a new type!'
                self._type = AttributeType(AttributeType.String)
        else:
            raise InvalidCloudioAttributeException(the_type)

    ######################################################################
    # Public API
    #
    def get_timestamp(self):
        return self._timestamp

    def set_static_value(self, value):
        """Initializes the static value

        This can be only done using static attributes (@StaticAttribute or @Static).
        The value of a static attribute can be changed as often as wanted, the only constraint is that the node
        containing the static attribute has not been registered within the endpoint.

        :param value: The initial value to set
        :return:
        """
        # TODO Check constraint
        # self._constraint.endpointWillChangeStatic()

        self._set_value_with_type_check(value)

    def get_parent(self):
        return self._parent

    def set_parent(self, parent):
        """Sets the parent of the attribute. Note that attributes can not be moved, so this method throws a runtime
           exception if someone tries to move the attribute to a new parent.
        """
        # If the attribute already has a parent (we are moving the attribute) then fail with a runtime exception.
        if self._parent:
            raise CloudioModificationException('The parent of an Attribute can never be changed ' +
                                               '(Attributes can not be moved)!')
        # assert isinstance(parent, CloudioAttributeContainer), 'Wrong type for parent attribute!'
        self._parent = parent

    def get_constraint(self):
        return self._constraint

    def set_constraint(self, constraint):
        """

        :param constraint:
        :type constraint: CloudioAttributeConstraint
        :return:
        """

        # Convert to AttributeConstraint if 'constraint' parameter is a string
        if isinstance(constraint, str):
            constraint = AttributeConstraint(constraint)

        assert isinstance(constraint, AttributeConstraint), 'Wrong type'

        if self._constraint:
            raise CloudioModificationException('The Attribute has already a constraint ' +
                                               '(Changing constraints is not allowed)!')
        # Set the constraint
        self._constraint = constraint

    def to_json(self, encoder):
        """Pick out the attributes we want to store / publish.
        """
        attr_dict = {
            'type': AttributeType.from_raw_type_to_string(self._value),
            'value': self._value,
            'constraint': self._constraint
        }

        # Name should not be added for @online message
        # attr_dict['name'] = self._name

        # Get the type of the value and convert it to cloud.io attribute type
        # attr_dict['timestamp'] = self._timestamp

        return encoder.default(attr_dict)
