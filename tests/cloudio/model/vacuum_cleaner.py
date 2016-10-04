# -*- coding: utf-8 -*-


class VacuumCleaner():
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