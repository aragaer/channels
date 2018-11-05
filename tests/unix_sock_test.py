import os
import shutil
import socket
import unittest

from tempfile import mkdtemp

from channels import EndpointClosedException, SocketChannel
from channels.poller import Poller
from utils import timeout


class UnixSocketTest:

    def prepare(self, *, buffering):
        self._dir = mkdtemp()
        self._sock_file = os.path.join(self._dir, "sock")
        self.addCleanup(shutil.rmtree, self._dir)
        self._server = socket.socket(socket.AF_UNIX)
        self._server.bind(self._sock_file)
        self._server.listen(0)
        self._poller = Poller(buffering=buffering)
        self._poller.add_server(self._server)
        self.addCleanup(self._poller.close_all)

    def verify(self, data, *expected):
        client = socket.socket(socket.AF_UNIX)
        client.connect(self._sock_file)
        self.addCleanup(client.close)

        with timeout(0.1):
            result = self._poller.poll(0.01)
        cl_chan = result[0][0][1]

        with timeout(0.1):
            client.send(data)

        with timeout(0.1):
            result = self._poller.poll(0.01)

        self.assertEqual(result,
                         [(a, cl_chan) for a in expected])


class UnixSocketBytesTest(unittest.TestCase, UnixSocketTest):

    def setUp(self):
        self.prepare(buffering=None)

    def test_all(self):
        for send in (b'hello', b'hello\n', b'hello\nworld\ntest'):
            with self.subTest(send=send, expect=send):
                self.verify(send, send)


class UnixSocketLinesTest(unittest.TestCase, UnixSocketTest):

    def setUp(self):
        self.prepare(buffering='line')

    def test_all(self):
        tc = {
            b'hello': (),
            b'hello\n': (b'hello\n',),
            b'hello\nworld\ntest': (b'hello\n', b'world\n')
        }
        for send, expect in tc.items():
            with self.subTest(send=send, expect=expect):
                self.verify(send, *expect)
