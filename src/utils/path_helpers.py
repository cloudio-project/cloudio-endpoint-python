# -*- coding: utf-8 -*-

import os

def prettify(pathName):
    """Makes all necessary stuff to get a usable path (specially under Windows)

    :param pathName: Path to make pretty
    :type pathName: str
    """

    if pathName:
        # Remove backslashes from path
        pathName = pathName.replace('\\', '/')

        if pathName[0] == '~':
            basePath = os.path.expanduser(pathName[0])
            remainingPath = pathName[2:] if pathName[1] == '/' else pathName[1:]
            pathName = os.path.join(basePath, remainingPath)

        # and again
        pathName = pathName.replace('\\', '/')

    return pathName
