#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example helps you to define arbitrary waveforms read out from a file."""

from time import sleep

from pipython import GCSDevice, pitools

CONTROLLERNAME = 'E-712'
STAGES = None  # connect stages to axes
REFMODE = None  # reference the connected stages

DATAFILE = r'wavegenerator_pnt.txt'
NUMCYLES = 2  # number of cycles for wave generator output
TABLERATE = 100  # duration of a wave table point in multiples of servo cycle times as integer


def main():
    """Connect controller, setup wave generator, move axes to startpoint and start wave generator."""
    with GCSDevice(CONTROLLERNAME) as pidevice:
        pidevice.InterfaceSetupDlg(key='sample')
        print('connected: %s' % pidevice.qIDN().strip())
        print('initialize connected stages...')
        pitools.startup(pidevice, stages=STAGES, refmode=REFMODE)
        runwavegen(pidevice)


def runwavegen(pidevice):
    """Read wave data, set up wave generator and run them.
    @type pidevice : pipython.gcscommands.GCSCommands
    """
    wavedata = readwavedata()
    axes = pidevice.axes[:len(wavedata)]
    assert len(wavedata) == len(axes), 'this sample requires {} connected axes'.format(len(wavedata))
    wavetables = range(1, len(wavedata) + 1)
    wavegens = range(1, len(wavedata) + 1)
    if pidevice.HasWCL():  # you can remove this code block if your controller does not support WCL()
        print('clear wave tables {}'.format(wavetables))
        pidevice.WCL(wavetables)
    for i, wavetable in enumerate(wavetables):
        print('write wave points of wave table {} and axis {}'.format(wavetable, axes[i]))
        pitools.writewavepoints(pidevice, wavetable, wavedata[i], bunchsize=10)
    if pidevice.HasWSL():  # you can remove this code block if your controller does not support WSL()
        print ('connect wave tables {} to wave generators {}'.format(wavetables, wavegens))
        pidevice.WSL(wavegens, wavetables)
    if pidevice.HasWGC():  # you can remove this code block if your controller does not support WGC()
        print('set wave generators {} to run for {} cycles'.format(wavegens, NUMCYLES))
        pidevice.WGC(wavegens, [NUMCYLES] * len(wavegens))
    if pidevice.HasWTR():  # you can remove this code block if your controller does not support WTR()
        print('set wave table rate to {} for wave generators {}'.format(TABLERATE, wavegens))
        pidevice.WTR(wavegens, [TABLERATE] * len(wavegens), interpol=[0] * len(wavegens))
    startpos = [wavedata[i][0] for i in range(len(wavedata))]
    print('move axes {} to start positions {}'.format(axes, startpos))
    pidevice.MOV(axes, startpos)
    pitools.waitontarget(pidevice, axes)
    print('start wave generators {}'.format(wavegens))
    pidevice.WGO(wavegens, mode=[1] * len(wavegens))
    while any(list(pidevice.IsGeneratorRunning(wavegens).values())):
        print '.',
        sleep(1.0)
    print('\nreset wave generators {}'.format(wavegens))
    pidevice.WGO(wavegens, mode=[0] * len(wavegens))
    print('done')


def readwavedata():
    """Read DATAFILE, must have a column for each wavetable.
    @return : Datapoints as list of lists of values.
    """
    print('read wave points from file {}'.format(DATAFILE))
    data = None
    with open(DATAFILE) as datafile:
        for line in datafile:
            items = line.strip().split()
            if data is None:
                print('found {} data columns in file'.format(len(items)))
                data = [[] for _ in range(len(items))]
            for i in range(len(items)):
                data[i].append(items[i])
    return data


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    main()
