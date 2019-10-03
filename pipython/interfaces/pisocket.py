#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Provide a socket."""

from logging import debug
import socket

from pipython.interfaces.pigateway import PIGateway

__signature__ = 0xd107f02a5957ea4ea84f7b6b3e0dca7e


class PISocket(PIGateway):
    """Provide a socket, can be used as context manager."""

    def __init__(self, host='localhost', port=50000):
        """Provide a connected socket.
        @param host : IP address as string, defaults to "localhost".
        @param port : IP port to use as integer, defaults to 50000.
        """
        debug('create an instance of PISocket(host=%s, port=%s)', host, port)
        self.__ip = (host, port)
        self.__buffer = ''
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect(self.__ip)
        self.__socket.setblocking(0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __str__(self):
        return 'PISocket(host=%s, port=%s)' % self.__ip

    @property
    def connectionid(self):
        """Get ID of current connection as integer."""
        return 0

    def send(self, msg):
        """Send 'msg' to the socket.
        @param msg : String to send.
        """
        totalsent = 0
        while totalsent < len(msg):
            tosend = msg[totalsent:]
            debug('PISocket.send: %r', tosend)
            sent = self.__socket.send(tosend.encode())
            if not sent:
                raise RuntimeError('socket connection broken')
            totalsent += sent

    @property
    def answersize(self):
        """Query socket and return the size of the answer as integer."""
        chunks = []
        while True:
            try:
                received = self.__socket.recv(2048)
            except IOError:
                break
            else:
                try:
                    received = received.decode('utf-8')
                except UnicodeDecodeError:
                    self.__buffer = received
                    chunks = []
                else:
                    chunks.append(received)
                finally:
                    debug('PISocket.received: %r', received)
        if chunks:
            try:
                self.__buffer += ''.join(chunks)
            except TypeError:
                self.__buffer += b''.join(chunks)
        return len(self.__buffer)

    def getanswer(self, bufsize):
        """Return received data.
        @param bufsize : Number of bytes to return.
        @return : Answer as string.
        """
        answer = self.__buffer[:bufsize]
        self.__buffer = self.__buffer[bufsize:]
        return answer

    def close(self):
        """Close socket."""
        debug('PISocket.close: close connection to %s:%s', self.__ip[0], self.__ip[1])
        self.__socket.shutdown(socket.SHUT_RDWR)
        self.__socket.close()
