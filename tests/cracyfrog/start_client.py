#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paths
from tests.cracyfrog.client.crazyfrog import CrazyFrogClient

paths.update_working_directory()


def main():
    client = CrazyFrogClient('~/.config/cloud.io/client/CrazyFrogClient.config')
    client.execute()


if __name__ == '__main__':
    main()
