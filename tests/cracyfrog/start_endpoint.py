#!/usr/bin/env python
# -*- coding: utf-8 -*-


from tests.cracyfrog import paths

paths.update_working_directory()


def main():
    from tests.cracyfrog.endpoint import CrazyFrogEndpoint

    crazyFrogEndpoint = CrazyFrogEndpoint()
    crazyFrogEndpoint.initialize()
    crazyFrogEndpoint.exec()


if __name__ == '__main__':
    main()
