import os
import shutil
import socket
import unittest

from tempfile import mkdtemp

from channels import EndpointClosedException, SocketChannel
from channels.poller import Poller
from utils import timeout


class UnixSocketTest(unittest.TestCase):

    def setUp(self):
        self._dir = mkdtemp()
        self._sock_file = os.path.join(self._dir, "sock")
        self.addCleanup(shutil.rmtree, self._dir)
        self._server = socket.socket(socket.AF_UNIX)
        self._server.bind(self._sock_file)
        self._server.listen()
        self._poller = Poller()
        self._poller.add_server(self._server)
        self.addCleanup(self._poller.close_all)

        self._client = socket.socket(socket.AF_UNIX)
        self._client.connect(self._sock_file)
        self.addCleanup(self._client.close)

        with timeout(0.1):
            result = self._poller.poll(0.01)
        self._cl_chan = result[0][0][1]

    def test_connect(self):
        with timeout(0.1):
            self._client.send(b"hello\n")

        with timeout(0.1):
            result = self._poller.poll(0.01)

        self.assertEqual(result, [(b"hello\n", self._cl_chan)])
