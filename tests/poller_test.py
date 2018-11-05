import socket
import unittest

from channels import Channel, EndpointClosedException
from channels.poller import Poller
from channels.testing import TestChannel

from utils import timeout


def _connect_and_get_client_channel(tc, poller):
    serv = socket.socket()
    serv.bind(('127.0.0.1', 0))
    serv.listen(0)
    tc.addCleanup(serv.close)

    addr, port = serv.getsockname()
    poller.add_server(serv)

    client = socket.create_connection((addr, port))
    result = list(poller.poll(0.01))  # accepts the client
    return client, result[0][0][1]


class PollerTest(unittest.TestCase):

    def setUp(self):
        self._poller = Poller()

    def tearDown(self):
        self._poller.close_all()

    def test_blocking_poll(self):
        with self.assertRaisesRegex(Exception, "timeout"), timeout(0.02):
            self._poller.poll()

    def test_timed_poll(self):
        with timeout(0.02):
            result = self._poller.poll(0.01)
        self.assertEqual(list(result), [])

    def test_timed_out_poll(self):
        with self.assertRaisesRegex(Exception, "timeout"), timeout(0.02):
            self._poller.poll(0.03)

    def test_poll_data(self):
        chan = TestChannel()
        self._poller.register(chan)
        chan.put(b'hello\n')

        with timeout(0.02):
            result = self._poller.poll()

        self.assertEqual(list(result), [(b'hello\n', chan)])

    def test_poll_no_data(self):
        chan = TestChannel()
        self._poller.register(chan)

        with timeout(0.02):
            result = self._poller.poll(0.01)

        self.assertEqual(list(result), [])

    def test_poll_accept(self):
        client, cl_chan = _connect_and_get_client_channel(self, self._poller)

        client.send(b'hello\n')

        result = self._poller.poll(0.01)
        self.assertEqual(list(result), [(b'hello\n', cl_chan)])

    def test_close_all_channels(self):
        chan = TestChannel()
        self._poller.register(chan)

        self._poller.close_all()

        with self.assertRaises(EndpointClosedException):
            chan.read()

    def test_close_all_servers(self):
        serv = socket.socket()
        serv.bind(('127.0.0.1', 0))
        serv.listen(0)
        self.addCleanup(serv.close)
        self._poller.add_server(serv)

        self._poller.close_all()

        with timeout(0.01), self.assertRaises(OSError):
            serv.accept()

    def test_unregister(self):
        chan = TestChannel()
        self._poller.register(chan)
        chan.put(b'hello\n')

        self._poller.unregister(chan)

        with self.assertRaisesRegex(Exception, "timeout"), timeout(0.02):
            self._poller.poll()

    def test_unregister_twice(self):
        chan = TestChannel()
        self._poller.register(chan)
        chan.put(b'hello\n')

        self._poller.unregister(chan)
        self._poller.unregister(chan)

    def test_closed(self):
        chan = TestChannel()
        self._poller.register(chan)

        chan.close()

        with timeout(0.01):
            result = self._poller.poll()

        self.assertEquals(result, [(b'', chan)])

    def test_disconnect(self):
        client, cl_chan = _connect_and_get_client_channel(self, self._poller)

        client.close()
        result = list(self._poller.poll(0.01))

        self.assertEqual(result, [(b'', cl_chan)])

    def test_unregister_on_disconnect(self):
        client, cl_chan = _connect_and_get_client_channel(self, self._poller)
        client.close()
        self._poller.poll(0.01)

        result = list(self._poller.poll(0.01))

        self.assertEqual(result, [])


class LineBufferedPollerTest(unittest.TestCase):

    def setUp(self):
        self._poller = Poller(buffering='line')
        self._client, self._cl_chan = _connect_and_get_client_channel(self, self._poller)

    def tearDown(self):
        self._poller.close_all()

    def test_partial_line(self):
        self._client.send(b'test')

        result = list(self._poller.poll(0.01))

        self.assertEqual(result, [])

        self._client.send(b'post\n')

        result = list(self._poller.poll(0.01))

        self.assertEqual(result, [(b'testpost\n', self._cl_chan)])

    def test_lines(self):
        self._client.send(b'test\nrest\n')

        result = list(self._poller.poll(0.01))

        self.assertEqual(result, [(b'test\n', self._cl_chan),
                                  (b'rest\n', self._cl_chan)])


class PollerBufferingTest(unittest.TestCase):

    def test_bytes_poller(self):
        poller = Poller()

        _, cl_chan = _connect_and_get_client_channel(self, poller)

        self.assertEqual(cl_chan.buffering, 'bytes')

    def test_line_poller(self):
        poller = Poller(buffering='line')

        _, cl_chan = _connect_and_get_client_channel(self, poller)

        self.assertEqual(cl_chan.buffering, 'line')
