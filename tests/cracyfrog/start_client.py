#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.cracyfrog.client.crazyfrog import CrazyFrogClient


def main():
    client = CrazyFrogClient('~/.config/cloud.io/client/CrazyFrogClient.config')
    client.execute()


if __name__ == '__main__':
    main()
