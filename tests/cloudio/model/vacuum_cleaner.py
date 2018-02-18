# -*- coding: utf-8 -*-

from six import iteritems
import logging
from cloudio.interface.attribute_listener import AttributeListener

logging.getLogger(__name__).setLevel(logging.INFO)

class VacuumCleaner(AttributeListener):
    """Class representing the 'real' vacuum cleaner.
    """

    log = logging.getLogger(__name__)

    def __init__(self):
        self.cloudioNode = None

    def setCloudioBuddy(self, cloudioNode):
        self.cloudioNode = cloudioNode

        cloudioParameterObject = self.cloudioNode.findObject(['Parameters',
                                                              'objects'])

        for attributeName, cloudioAttribute in iteritems(cloudioParameterObject.getAttributes()):
            self._createAttribute(attributeName, cloudioAttribute)
            cloudioAttribute.addListener(self)

    def _createAttribute(self, attributeName, cloudioAttribute):
        """

        :param attributeName: The attribute name given by cloud.iO
        :type attributeName: str
        :param cloudioAttribute: The cloud.iO attribute
        :return:
        """
        internalAttributeName = self._convertToInternalAttributeName(attributeName)

        setattr(self, internalAttributeName, cloudioAttribute.getValue())

    def _convertToInternalAttributeName(self, cloudioAttributeName):
        internalAttributeName = cloudioAttributeName
        if cloudioAttributeName.startswith('set'):
            internalAttributeName = '_' + cloudioAttributeName[3:3 + 1].lower() + cloudioAttributeName[4:]
        return internalAttributeName


    ######################################################################
    # AttributeListener interface implementations
    #
    # Used to get informed about attribute value changes in the cloud
    # representation of the node/device.
    #
    def attributeHasChanged(self, attribute):
        """This method is called upon an attribute has been changed.

        :param attribute Attribute that has changed.
        """
        internalAttributeName = self._convertToInternalAttributeName(attribute.getName())
        print('VacuumCleaner attr changed: ' + str(attribute.getValue()))

        # Check if we have an attribute with the same name
        if hasattr(self, internalAttributeName):
            setattr(self, internalAttributeName, attribute.getValue())
        else:
            self.log.warning('Attribute \'' + internalAttributeName + '\' not found in ' + self.__class__.__name__)
