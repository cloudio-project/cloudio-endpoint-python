#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import unittest
from tests.cloudio.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/cloudio/{this_file}.py'


class TestCloudioEndpoint(unittest.TestCase):
    """Tests cloudio endpoint class.
    """

    log = logging.getLogger(__name__)

    def test_process_received_message(self):
        from cloudio.endpoint import CloudioEndpoint

        endpoint = CloudioEndpoint('test-endpoint', locations='path:../config/')

        msg = ''
        with self.assertLogs() as log:
            endpoint._processReceivedMessage(msg)
            self.assertTrue("ERROR:cloudio.endpoint.endpoint:'str' object has no attribute 'payload'" in log.output[0])


if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
