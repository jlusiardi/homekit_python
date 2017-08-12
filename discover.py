#!/usr/bin/env python3

import argparse

from homekit import discover_homekit_devices


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit discover app - list all HomeKit devices on the same network')
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()

    discover_homekit_devices()
