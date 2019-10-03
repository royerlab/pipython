#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Move all axes to targets read from CSV file 'DATAFILE'."""

from time import sleep

from pipython import GCSDevice, pitools

CONTROLLERNAME = 'C-863.11'
STAGES = ('M-111.1DG',)  # connect stages to axes
REFMODE = ('FNL',)  # reference the connected stages

DATAFILE = 'targets_from_csv.csv'
RELAXTIME = 200  # time in ms to wait after each motion command or 0 to wait for on target state
SEPARATOR = ','


def main():
    """Connect controller, setup stages and move all axes to targets read from CSV file 'DATAFILE'."""
    with GCSDevice(CONTROLLERNAME) as pidevice:
        pidevice.InterfaceSetupDlg(key='sample')
        print('connected: {}'.format(pidevice.qIDN().strip()))
        print('initialize connected stages...')
        pitools.startup(pidevice, stages=STAGES, refmode=REFMODE)
        movetotargets(pidevice)


def movetotargets(pidevice):
    """Move all axes to targets read from CSV file 'DATAFILE'.
    Add further columns if there are more than 6 axes connected.
    @type pidevice : pipython.gcscommands.GCSCommands
    """
    with open(DATAFILE, 'rb') as fobj:
        for line in fobj:
            targets = line.split(SEPARATOR)[:pidevice.numaxes]
            print 'targets: {}'.format(', '.join(targets))
            targets = [float(x) for x in targets]
            pidevice.MOV(pidevice.axes, targets)
            sleep(RELAXTIME / 1000.)
            if not RELAXTIME:
                pitools.waitontarget(pidevice)
    print('done')


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    main()
