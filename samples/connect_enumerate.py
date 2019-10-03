#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example shows how to search for controllers."""

from pipython import GCSDevice


def main():
    """Search controllers on interface, show dialog and connect a controller."""
    with GCSDevice() as pidevice:
        print('search for controllers...')
        devices = pidevice.EnumerateTCPIPDevices()
        # devices = EnumerateUSBDevices()
        for i, device in enumerate(devices):
            print('{} - {}'.format(i, device))
        item = int(input('select device to connect: '))
        pidevice.ConnectTCPIPByDescription(devices[item])
        # ConnectUSB(devices[item])
        print('connected: {}'.format(pidevice.qIDN().strip()))


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    main()
