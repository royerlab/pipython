#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Provide a device, connected via the PI GCS DLL."""

from pipython import gcserror
from pipython.gcsmessages import GCSMessages
from pipython.gcscommands import GCSCommands
from pipython.interfaces.gcsdll import GCSDll

__signature__ = 0x80fd420af745e8adb22e504de4ef6adb


# Invalid method name pylint: disable=C0103
# Too many public methods pylint: disable=R0904
class GCSDevice(GCSCommands):
    """Provide a device connected via the PI GCS DLL, can be used as context manager."""

    def __init__(self, devname='', gcsdll=''):
        """Provide a device, connected via the PI GCS DLL.
        @param devname : Name of device, chooses according DLL which defaults to PI_GCS2_DLL.
        @param gcsdll : Name or path to GCS DLL to use, overwrites 'devname'.
        """
        self.dll = GCSDll(devname, gcsdll)
        messages = GCSMessages(self.dll)
        super(GCSDevice, self).__init__(messages)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dll.unload()

    @property
    def dcid(self):
        """Get ID of current daisy chain connection as integer."""
        return self.dll.dcid

    @property
    def dllpath(self):
        """Get full path to GCS DLL."""
        return self.dll.dllpath

    def unload(self):
        """Close connection to device and daisy chain and unload GCS DLL."""
        del self.funcs
        del self.devname
        del self.axes
        self.dll.unload()

    def close(self):
        """Close connection to device and daisy chain."""
        del self.funcs
        del self.devname
        del self.axes
        self.dll.close()

    def GetError(self):
        """Get current controller error.
        @return : Current error code as integer.
        """
        return self.qERR()

    @staticmethod
    def TranslateError(errval):
        """Translate GCS error number into readable error message.
        @param errval: GCSError value as integer.
        @return: GCSError message as string.
        """
        return gcserror.translate_error(errval)

    def GetAsyncBuffer(self, firstline=1, lastline=0, numtables=1):
        """Query all available data points, return list with 'numtables' columns.
        DEPRECATED: Use GCSMessages.bufdata instead.
        Buffer is used by qDRR(), qDDL(), qGWD(), qTWS(), qJLT() and qHIT().
        @param firstline : Optional, but must be >= 1 and smaller than 'lastline'.
        @param lastline : Optional, defaults to query all available data points.
        @param numtables : Arrange data into 'numtables' columns, defaults to "1".
        @return: List of data points as float with 'numtables' columns.
        """
        return self.dll.GetAsyncBuffer(firstline, lastline, numtables)

    def GetAsyncBufferIndex(self):
        """Get current index used for the internal buffer.
        DEPRECATED: Use GCSMessages.bufindex instead.
        @return: Buffer index as integer.
        """
        return self.dll.GetAsyncBufferIndex()

    def IsConnected(self):
        """Return True if a device is connected."""
        return self.dll.IsConnected()

    def GetInterfaceDescription(self):
        """Get textual description of actual interface connection."""
        return self.dll.GetInterfaceDescription()

    def InterfaceSetupDlg(self, key=''):
        """Open dialog to select the interface.
        @param key: Optional key name as string to store the settings in the Windows registry.
        """
        self.dll.InterfaceSetupDlg(key)

    def ConnectRS232(self, comport, baudrate):
        """Open an RS-232 connection to the device.
        @param comport: Port to use as integer (1 means "COM1") or device name ("dev/ttys0") as str.
        @param baudrate: Baudrate to use as integer.
        """
        self.dll.ConnectRS232(comport, baudrate)

    def ConnectTCPIP(self, ipaddress, ipport=50000):
        """Open a TCP/IP connection to the device.
        @param ipaddress: IP address to connect to as string.
        @param ipport: Port to use as integer, defaults to 50000.
        """
        self.dll.ConnectTCPIP(ipaddress, ipport)

    def ConnectTCPIPByDescription(self, description):
        """Open a TCP/IP connection to the device using the device 'description'.
        @param description: One of the identification strings listed by EnumerateTCPIPDevices().
        """
        self.dll.ConnectTCPIPByDescription(description)

    def ConnectUSB(self, serialnum):
        """Open an USB connection to a device.
        @param serialnum: Serial number of device or one of the
        identification strings listed by EnumerateUSB().
        """
        self.dll.ConnectUSB(serialnum)

    def ConnectNIgpib(self, board, device):
        """Open a connection from a NI IEEE 488 board to the device.
        @param board: GPIB board ID as integer.
        @param device: The GPIB device ID of the device as integer.
        """
        self.dll.ConnectNIgpib(board, device)

    def ConnectPciBoard(self, board):
        """Open a PCI board connection.
        @param board : PCI board number as integer.
        """
        self.dll.ConnectPciBoard(board)

    def EnumerateUSB(self, mask=''):
        """Get identification strings of all USB connected devices.
        @param mask: String to filter the results for certain text.
        @return: Found devices as list of strings.
        """
        return self.dll.EnumerateUSB(mask)

    def EnumerateTCPIPDevices(self, mask=''):
        """Get identification strings of all TCP connected devices.
        @param mask: String to filter the results for certain text.
        @return: Found devices as list of strings.
        """
        return self.dll.EnumerateTCPIPDevices(mask)

    def OpenRS232DaisyChain(self, comport, baudrate):
        """Open an RS-232 daisy chain connection.
        To get access to a daisy chain device you have to call ConnectDaisyChainDevice().
        @param comport: Port to use as integer (1 means "COM1").
        @param baudrate: Baudrate to use as integer.
        @return: Found devices as list of strings.
        """
        return self.dll.OpenRS232DaisyChain(comport, baudrate)

    def OpenUSBDaisyChain(self, description):
        """Open a USB daisy chain connection.
        To get access to a daisy chain device you have to call ConnectDaisyChainDevice().
        @param description: Description of the device returned by EnumerateUSB().
        @return: Found devices as list of strings.
        """
        return self.dll.OpenUSBDaisyChain(description)

    def OpenTCPIPDaisyChain(self, ipaddress, ipport=50000):
        """Open a TCPIP daisy chain connection.
        To get access to a daisy chain device you have to call ConnectDaisyChainDevice().
        @param ipaddress: IP address to connect to as string.
        @param ipport: Port to use as integer, defaults to 50000.
        @return: Found devices as list of strings.
        """
        return self.dll.OpenTCPIPDaisyChain(ipaddress, ipport)

    def ConnectDaisyChainDevice(self, deviceid, daisychainid=None):
        """Connect device with 'deviceid' on the daisy chain 'daisychainid'.
        Daisy chain has to be connected before, see Open<interface>DaisyChain() functions.
        @param daisychainid : Daisy chain ID as int from the daisy chain master instance or None.
        @param deviceid : Device ID on the daisy chain as integer.
        """
        self.dll.ConnectDaisyChainDevice(deviceid, daisychainid)

    def CloseConnection(self):
        """Reset axes property and close connection to the device."""
        del self.axes
        self.dll.CloseConnection()

    def CloseDaisyChain(self):
        """Close all connections on daisy chain and daisy chain connection itself."""
        self.dll.CloseDaisyChain()
