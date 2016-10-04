# -*- coding: utf-8 -*-

import sys, os, time
import logging
import traceback
from xml.dom import minidom
from utils import path_helpers

from cloudio.endpoint import CloudioEndpoint
from cloudio.cloudio_runtime_node import CloudioRuntimeNode
from cloudio.cloudio_runtime_object import CloudioRuntimeObject

# Enable logging
logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

class VacuumCleanerConnector(object):
    """Creates the cloud.iO endpoint according to the model file.

    After creation the endpoint goes online and is available in the cloud.
    """
    log = logging.getLogger(__name__)

    def __init__(self, cloudioEndpointName):
        self.endpoint = CloudioEndpoint(cloudioEndpointName)

    def getEndpointName(self):
        return self.endpoint.getName()

    def createModel(self, xmlModelFile):
        try:
            pathName = path_helpers.prettify(xmlModelFile)

            self.log.info('Reading cloud.iO enpoint model from \'%s\'' % pathName)

            pathName = os.path.abspath(pathName)    # Convert to absolute path to make isfile() happy

            # Check if config file is present
            if os.path.isfile(pathName):
                # Parse XML config file
                xmlConfigFile = minidom.parse(pathName)

                if xmlConfigFile:
                    configList = xmlConfigFile.getElementsByTagName(u'config')
                    """:type : list of minidom.Element"""

                    for config in configList:
                        deviceTypeList = config.getElementsByTagName(u'deviceType')
                        """:type : list of minidom.Element"""

                        for deviceType in deviceTypeList:
                            """:type : list of minidom.Element"""
                            print u'Parsing elements for device: ' + deviceType.getAttribute('typeId')
                            self._parseDeviceTypeFromXmlDomElement(deviceType)
            else:
                raise RuntimeError(u'Missing configuration file: %s' % pathName)

        except Exception as e:
            traceback.print_exc()

        # After the endpoint is fully created the presents can be announced
        self.endpoint.announce()

    def _parseDeviceTypeFromXmlDomElement(self, deviceType):
        """Parses a device type from an xml dom element

        :param deviceType:
        :type deviceType: minidom.Element
        :return:
        """
        assert deviceType.tagName == u'deviceType', u'Wrong DOM element name'

        nodeName = deviceType.getAttribute(u'typeId')
        cloudioRuntimeNode = CloudioRuntimeNode()
        cloudioRuntimeNode.declareImplementedInterface(u'NodeInterface')

        objectList = deviceType.getElementsByTagName(u'object')
        """:type : list of minidom.Element"""
        for obj in objectList:
            objectName = obj.getAttribute(u'id')
            # Create cloud.iO object
            cloudioRuntimeObject = CloudioRuntimeObject()
            # Add object to the node
            cloudioRuntimeNode.addObject(objectName, cloudioRuntimeObject)

            # Get the attributes for the object node
            attributeList = obj.getElementsByTagName(u'attribute')
            for attribute in attributeList:
                self._parseAttributeFromXmlDomElement(cloudioRuntimeObject, attribute)

        assert nodeName, u'No node name given!'
        assert cloudioRuntimeNode, u'No cloud.iO node object given!'
        self.endpoint.addNode(nodeName, cloudioRuntimeNode)

    @classmethod
    def _parseAttributeFromXmlDomElement(cls, cloudioRuntimeObject, attributeElement):
        """Parses an attribute from an xml dom element

        :parame cloudioRuntimeObject:
        :type cloudioRuntimeObject: CloudioRuntimeObject
        :param attributeElement:
        :type attributeElement: minidom.Element
        :return:
        """
        assert attributeElement.tagName == u'attribute', u'Wrong DOM element name'

        theName = attributeElement.getAttribute(u'id')
        strType = attributeElement.getAttribute(u'template')
        strConstraint = attributeElement.getAttribute(u'constraint')

        # TODO Get options

        # TODO Convert constraint from 'string' to CloudioAttributeConstraint

        theType = None

        if strType.lower() == 'bool' or strType.lower() == 'boolean':
            theType = bool
        elif strType.lower() in ('short', 'long', 'integer'):
            theType = int
        elif strType.lower() == 'float' or strType.lower() == 'double' or strType.lower() == 'number':
            theType = float
        elif strType.lower() == 'str' or strType.lower() == 'string':
            theType = str

        assert theType, u'Attribute type unknown or not set!'

        cloudioRuntimeObject.addAttribute(theName, theType, strConstraint)

