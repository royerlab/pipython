PI Python Libraries
===================

PIPython is a collection of Python modules to access a PI device and process
GCS data. It can be used with Python 2.7+ and 3.4+ on Windows, Linux and OS X
and without the GCS DLL also on any other platform.

Version: 1.3.5.37


Quickstart
----------

Communicate to a PI device via *GCSDevice* which wraps the GCS commands
and provides methods to connect to the device. Call *GCSDevice* with the
controller name as argument::

    from pipython import GCSDevice
    gcs = GCSDevice('C-884')
    gcs.InterfaceSetupDlg()
    print gcs.qIDN()
    gcs.CloseConnection()


Installation
------------

By using PIPython you agree to the license agreement, see the provided file::

    license.md

Unzip the file PIPython.zip, open a command entry (console) and run::

    python setup.py install

For further reading see the provided documentation and samples in the *docs*
and *samples* subdirectories in the provided ZIP file.

We appreciate your feedback at::

    support-software@pi.ws
