#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import unittest
from tests.cloudio.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/cloudio/{this_file}.py'

VACUUM_CLEANER_NAME = 'VacuumCleanerEndpoint'


class TestCloudioEndpointVersion(unittest.TestCase):
    """Tests endpoint version.
    """

    log = logging.getLogger(__name__)

    def test_version_01(self):
        from cloudio import endpoint

        print(endpoint.version)

        self.assertTrue(isinstance(endpoint.version, str))
        self.assertIsNot(endpoint.version, '')
        self.assertTrue(len(endpoint.version.split('.')) == 3)  # Want to see 'x.y.z'

    def test_version_02(self):
        from cloudio.endpoint import version

        print(version)

        self.assertTrue(isinstance(version, str))
        self.assertIsNot(version, '')
        self.assertTrue(len(version.split('.')) == 3)  # Want to see 'x.y.z'


if __name__ == '__main__':

    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
