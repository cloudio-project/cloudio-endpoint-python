#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import uuid
from cloudio.endpoint import CloudioEndpoint

def main():

    endpointUuid = ' '.join(sys.argv[1:]) or uuid.uuid4()

    ciEndpoint = CloudioEndpoint(endpointUuid)

    while (True):
        time.sleep(1)

if __name__ == '__main__':
    main()