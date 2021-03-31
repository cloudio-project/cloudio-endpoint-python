#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paths

paths.update_working_directory()


def main():
    from tests.crazyfrog.client.crazyfrog import CrazyFrogClient

    client = CrazyFrogClient('~/.config/cloud.io/client/CrazyFrogClient.config')
    client.execute()


if __name__ == '__main__':
    main()
