#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Collection of helpers for using a PI device."""

from logging import debug
from time import sleep, time

from pipython import GCSError, gcserror

__signature__ = 0xb084e4568e4bda2b202a65b455b9fdd0


class FrozenClass(object):  # Too few public methods pylint: disable=R0903
    """Freeze child class when self.__isfrozen is set, i.e. values of already existing properties can still
    be changed but no new properties can be added.
    """
    __isfrozen = False

    def __setattr__(self, key, value):
        if self.__isfrozen and key not in dir(self):  # don't use hasattr(), it returns False on any exception
            raise TypeError('%r is immutable, cannot add %r' % (self, key))
        object.__setattr__(self, key, value)

    def _freeze(self):
        """After this method has been called the child class denies adding new properties."""
        self.__isfrozen = True


class GCSRaise(object):  # Too few public methods pylint: disable=R0903
    """Context manager that asserts raising of specific GCSError(s).
    @param gcserrorid : GCSError ID or iterable of IDs that are expected to be raised as integer.
    @param mustraise : If True an exception must be raised, if False an exception can be raised.
    """

    def __init__(self, gcserrorid, mustraise=True):
        debug('create an instance of GCSRaise(gcserrorid=%s, mustraise=%s', gcserrorid, mustraise)
        self.__expected = gcserrorid if hasattr(gcserrorid, '__iter__') else [gcserrorid]
        self.__mustraise = mustraise and gcserrorid

    def __enter__(self):
        return self

    def __exit__(self, exctype, excvalue, _exctraceback):

        gcsmsg = '%r' % gcserror.translate_error(excvalue)
        if exctype == GCSError:
            if excvalue in self.__expected:
                debug('expected GCSError %s was raised', gcsmsg)
                return True  # do not re-raise
        if not self.__mustraise and excvalue is None:
            debug('no error was raised')
            return True  # do not re-raise
        expected = ', '.join([gcserror.translate_error(errval) for errval in self.__expected])
        msg = 'expected %r but raised was %s' % (expected, gcsmsg)
        raise ValueError(msg)


def startup(pidevice, stages=None, refmode=None):
    """Define 'stages', stop all, enable servo on all connected axes and reference them with 'refmode'.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param stages : Name of stages to initialize as string or list or None to skip.
    @param refmode : Name of referencing commands as string or list or None to skip.
    If list then one entry for each axis, None to skip an axis. If it is a single string
    all axes will be referenced with this command.
    """
    if stages:
        allaxes = pidevice.qSAI_ALL()
        stages = stages if isinstance(stages, (list, tuple)) else [stages]
        stages = stages[:len(allaxes)]
        allaxes = allaxes[:len(stages)]
        pidevice.CST(allaxes, stages)
    if pidevice.HasINI():
        pidevice.INI()
    if pidevice.HasONL():
        pidevice.ONL(list(range(1, pidevice.numaxes + 1)), [True] * pidevice.numaxes)
    stopall(pidevice)
    pidevice.SVO(pidevice.axes, [True] * len(pidevice.axes))
    waitontarget(pidevice, axes=pidevice.axes)
    referencedaxes = []
    if refmode:
        refmode = refmode if isinstance(refmode, (list, tuple)) else [refmode] * pidevice.numaxes
        refmode = refmode[:pidevice.numaxes]
        reftypes = set(refmode)
        for reftype in reftypes:
            if reftype is None:
                continue
            axes = [pidevice.axes[i] for i in range(len(refmode)) if refmode[i] == reftype]
            getattr(pidevice, reftype.upper())(axes)
            referencedaxes += axes
    waitontarget(pidevice, axes=referencedaxes)


def writewavepoints(pidevice, wavetable, wavepoints, bunchsize=None):
    """Write 'wavepoints' for 'wavetable' in bunches of 'bunchsize'.
    The 'bunchsize' is device specific. Please refer to the controller manual.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param wavetable : Wave table ID as integer.
    @param wavepoints : Single wavepoint as float convertible or list of them.
    @param bunchsize : Number of wavepoints in a single bunch or None to send all 'wavepoints' in a single bunch.
    """
    wavepoints = wavepoints if hasattr(wavepoints, '__iter__') else [wavepoints]
    if bunchsize is None:
        bunchsize = len(wavepoints)
    for startindex in range(0, len(wavepoints), bunchsize):
        bunch = wavepoints[startindex:startindex + bunchsize]
        pidevice.WAV_PNT(table=wavetable, firstpoint=startindex + 1, numpoints=len(bunch),
                         append='&' if startindex else 'X', wavepoint=bunch)


def getaxeslist(pidevice, axes):
    """Return list of 'axes'.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axis as string or list of them or None for all axes.
    @return : List of axes from 'axes' or all axes or empty list.
    """
    axes = pidevice.axes if axes is None else axes
    if not axes:
        return []
    if not hasattr(axes, '__iter__'):
        axes = [axes]
    return axes


def ontarget(pidevice, axes):
    """Return dictionary of on target states for open- or closedloop 'axes'.
    If qOSN is not supported open loop axes will return True.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axis or list of axes to get values for or None for all axes.
    @return : Dictionary of boolean ontarget states of 'axes'.
    """
    axes = getaxeslist(pidevice, axes)
    if not axes:
        return {}
    servo = pidevice.qSVO(axes)
    closedloopaxes = [axis for axis in axes if servo[axis]]
    openloopaxes = [axis for axis in axes if not servo[axis]]
    isontarget = {}
    if closedloopaxes:
        if pidevice.HasqONT():
            isontarget.update(pidevice.qONT(closedloopaxes))
        elif pidevice.HasIsMoving():
            ismoving = pidevice.IsMoving(closedloopaxes).values()
            isontarget.update(dict(list(zip(closedloopaxes, [not x for x in ismoving]))))
    if openloopaxes:
        if pidevice.HasqOSN():
            stepsleft = pidevice.qOSN(openloopaxes).values()
            isontarget.update(dict(list(zip(openloopaxes, [x == 0 for x in stepsleft]))))
        else:
            isontarget.update(dict(list(zip(openloopaxes, [True] * len(openloopaxes)))))
    return isontarget


def waitonready(pidevice, timeout=60, predelay=0, polldelay=0.1):
    """Wait until controller is on "ready" state and finally query controller error.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param timeout : Timeout in seconds as float, defaults to 60 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param polldelay : Delay time between polls in seconds as float.
    """
    sleep(predelay)
    if not pidevice.HasIsControllerReady():
        return
    maxtime = time() + timeout
    while not pidevice.IsControllerReady():
        if time() > maxtime:
            raise SystemError('waitonready() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    pidevice.checkerror()


# Too many arguments (6/5) pylint: disable=R0913
def waitontarget(pidevice, axes=None, timeout=60, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'axes' are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axes to wait for as string or list, or None to wait for all axes.
    @param timeout : Timeout in seconds as float, defaults to 60 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    axes = getaxeslist(pidevice, axes)
    if not axes:
        return
    waitonready(pidevice, timeout, predelay)
    maxtime = time() + timeout
    while not all(list(pidevice.qONT(axes).values())):
        if time() > maxtime:
            raise SystemError('waitontarget() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    sleep(postdelay)


def waitonfastalign(pidevice, name=None, timeout=60, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'axes' are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param name : Name of the process as string or list.
    @param timeout : Timeout in seconds as float, defaults to 60 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    waitonready(pidevice, timeout, predelay)
    maxtime = time() + timeout
    while any(list(pidevice.qFRP(name).values())):
        if time() > maxtime:
            raise SystemError('waitonfastalign() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    sleep(postdelay)


def waitonautozero(pidevice, axes=None, timeout=60, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'axes' are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axes to wait for as string or list, or None to wait for all axes.
    @param timeout : Timeout in seconds as float, defaults to 60 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    axes = getaxeslist(pidevice, axes)
    if not axes:
        return
    waitonready(pidevice, timeout, predelay)
    maxtime = time() + timeout
    while not all(list(pidevice.qATZ(axes).values())):
        if time() > maxtime:
            raise SystemError('waitonautozero() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    sleep(postdelay)


# Too many arguments (6/5) pylint: disable=R0913
def waitonwalk(pidevice, channels, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until qOSN for channels is zero.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param channels : Channel or list of channels to wait for motion to finish.
    @param timeout : Timeout in seconds as float, defaults to 300 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    channels = channels if isinstance(channels, (list, tuple)) else [channels]
    maxtime = time() + timeout
    waitonready(pidevice, timeout, predelay)
    while not all(list(x == 0 for x in list(pidevice.qOSN(channels).values()))):
        if time() > maxtime:
            stopall(pidevice)
            raise SystemError('waitonwalk() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    sleep(postdelay)


# Too many arguments (6/5) pylint: disable=R0913
def waitonoma(pidevice, axes=None, timeout=300, predelay=0, polldelay=0.1):
    """Wait on the end of an open loop motion of 'axes'.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axis as string or list of them to get values for or None to query all axes.
    @param timeout : Timeout in seconds as float, defaults to 300 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param polldelay : Delay time between polls in seconds as float.
    """
    axes = getaxeslist(pidevice, axes)
    numsamples = 5
    positions = []
    maxtime = time() + timeout
    waitonready(pidevice, timeout, predelay)
    while True:
        positions.append(list(pidevice.qPOS(axes).values()))
        positions = positions[-numsamples:]
        if len(positions) < numsamples:
            continue
        isontarget = True
        for vals in zip(*positions):
            isontarget &= 0.01 > sum([abs(vals[i] - vals[i + 1]) for i in range(len(vals) - 1)])
        if isontarget:
            return
        if time() > maxtime:
            stopall(pidevice)
            raise SystemError('waitonoma() timed out after %.1f seconds' % timeout)
        sleep(polldelay)


# Too many arguments (6/5) pylint: disable=R0913
def waitontrajectory(pidevice, trajectories=None, timeout=180, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'trajectories' are done and all axes are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param trajectories : Integer convertible or list of them or None for all trajectories.
    @param timeout : Timeout in seconds as floatfor trajectory and motion, defaults to 180 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    maxtime = time() + timeout
    waitonready(pidevice, timeout, predelay)
    while any(list(pidevice.qTGL(trajectories).values())):
        if time() > maxtime:
            stopall(pidevice)
            raise SystemError('waitontrajectory() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    waitontarget(pidevice, timeout=timeout, predelay=0, postdelay=postdelay, polldelay=polldelay)


def stopall(pidevice):
    """Stop motion of all axes and mask the "error 10" warning.
    @type pidevice : pipython.gcscommands.GCSCommands
    """
    try:
        pidevice.StopAll()
    except GCSError as exc:
        if gcserror.E10_PI_CNTR_STOP != exc:  # error 10 is just a warning that the device has been stopped
            raise
