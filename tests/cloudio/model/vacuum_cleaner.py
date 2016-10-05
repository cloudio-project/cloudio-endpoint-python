# -*- coding: utf-8 -*-

from cloudio.interface.attribute_listener import AttributeListener

class VacuumCleaner(AttributeListener):
    """Class representing the 'real' vacuum cleaner.
    """

    def __init__(self):
        self.cloudioNode = None

    def setCloudioBuddy(self, cloudioNode):
        self.cloudioNode = cloudioNode

        cloudioParameterObject = self.cloudioNode.findObject(['Parameters',
                                                              'objects'])

        for attributeName, cloudioAttribute in cloudioParameterObject.getAttributes().iteritems():
            self._createAttribute(attributeName, cloudioAttribute)
            cloudioAttribute.addListener(self)

    def _createAttribute(self, attributeName, cloudioAttribute):
        """

        :param attributeName: The attribute name given by cloud.iO
        :type attributeName: str
        :param cloudioAttribute: The cloud.iO attribute
        :return:
        """
        internalAttributeName = attributeName

        if attributeName.startswith('set'):
            internalAttributeName = '_' + attributeName[3:3+1].lower() + attributeName[4:]

        setattr(self, internalAttributeName, cloudioAttribute.getValue())


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

        # Check if we have an attribute with the same name
        if hasattr(self, attribute.getName()):
            setattr(self, attribute.getName(), attribute.getValue())
        else:
            self.log.warning('Attribute \'' + attribute.getName() + '\' not found in ' + self.__class__.__name__)
