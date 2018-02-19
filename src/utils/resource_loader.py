# -*- coding: utf-8 -*-

import six
import os
if six.PY2:
    import urlparse                         # pip install urllib3
else:
    import urllib.parse as urlparse
from os.path import expanduser
from configobj import ConfigObj         # pip install configobj

class ResourceLoader():

    @classmethod
    def loadFromLocations(self, filename, locations):
        """
        :rtype filename: str
        :rtype locations: [str]
        :return: {}
        """

        for location in locations:
            url = urlparse.urlparse(location)

            if url.scheme == 'home':
                basePath = expanduser('~').replace('\\','/') + url.path
                filePath = os.path.join(basePath, filename)

                if os.path.isfile(filePath):
                    properties = ConfigObj(filePath)
                    return properties
            elif url.scheme == 'file':
                    filePath = url.path + filename
                    if os.path.isfile(filePath):
                        properties = ConfigObj(filePath)
                        return properties
            elif url.scheme == 'http' or \
                 url.scheme == 'https':
                if not location.endswith('/'):
                    location += '/'
                filePath = location + filename
                try:
                    file = urllib.urlopen(filePath)
                    print(file)
                except:
                    pass

        return {}
