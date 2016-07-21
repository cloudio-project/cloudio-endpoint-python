# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class Uuid(object):
    """Interface to represent an object as a uuid (Universally Unique Identifier).

    An object implementing the UniqueIdentifiable interface has to return an object implementing
    the Uuid interface as return value of the method getUuid().

    The only mandatory operation such an Uuid has to offer is to allow it to be compared it with other UUIDs for
    equality. However it is recommended that the standard Object's toString() method return a unique string as well, in
    order to simplify development and trouble-shooting, but this is not actually required.

    see UniqueIdentifiable
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def equals(self, other):
        """Returns true if the UUID is equal to the given one, false otherwise.

        :param other: The UUID to check equality with.
        :type other: Uuid
        :return: True if equal, false otherwise.
        :rtype: bool
        """
        pass

    @abstractmethod
    def toString(self):
        """Should return a serialisation of the UUID. Note that the serialisation should be unique too!

        :return: Serialized UUID.
        :rtype: str
        """
        pass

    @abstractmethod
    def isValid(self):
        """Returns true if the UUID holds a valid UUID or false if the UUID should be considered invalid.

            :return: True if the UUID is valid, false otherwise.
            :rtype: bool
        """
        pass