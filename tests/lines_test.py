import os
import socket
import unittest

from channels import EndpointClosedException, PipeChannel, SocketChannel
from channels.testing import TestChannel


class LineBufferedTest:

    def feed(self, data):
        pass

    def test_buffering_property(self):
        self.assertEqual(self._chan.buffering, 'line')

    def test_write_line(self):
        self.feed(b'test\n')

        self.assertEqual(self._chan.read(), b'test\n')

    def test_write_partial(self):
        self.feed(b'te')

        self.assertEqual(self._chan.read(), b'')

    def test_write_two_step(self):
        self.feed(b'te')

        self.assertEqual(self._chan.read(), b'')

        self.feed(b'st\n')

        self.assertEqual(self._chan.read(), b'test\n')
        self.assertEqual(self._chan.read(), b'')

    def test_write_more_than_one_line(self):
        self.feed(b'a\nb\n')

        self.assertEqual(self._chan.read(), b'a\n')
        self.assertEqual(self._chan.read(), b'b\n')

    def test_read_last_line(self):
        self.feed(b'\ntest')

        self.assertEqual(self._chan.read(), b'\n')

        self._chan.close()

        self.assertEqual(self._chan.read(), b'test')

    def test_read_including_last_line(self):
        self.feed(b'\nhello\nworld')

        self.assertEqual(self._chan.read(), b'\n')

        self._chan.close()

        self.assertEqual(self._chan.read(), b'hello\n')
        self.assertEqual(self._chan.read(), b'world')
        with self.assertRaises(EndpointClosedException):
            print(self._chan.read())


class LineBufferedSocketChannelTest(unittest.TestCase, LineBufferedTest):

    def setUp(self):
        self._server, self._client = socket.socketpair()
        self.addCleanup(self._server.close)
        self.addCleanup(self._client.close)
        self._chan = SocketChannel(self._client, buffering='line')

    def feed(self, data):
        self._server.send(data)


class LineBufferedPipeChannelTest(unittest.TestCase, LineBufferedTest):

    def setUp(self):
        self._faucet, sink_fd = os.pipe()
        self._chan = PipeChannel(faucet=self._faucet, buffering='line')
        self._sink = os.fdopen(sink_fd, mode='wb')
        self.addCleanup(self._chan.close)
        self.addCleanup(self._sink.close)

    def feed(self, data):
        self._sink.write(data)
        self._sink.flush()


class LineBufferedTestChannelTest(unittest.TestCase, LineBufferedTest):

    def setUp(self):
        self._chan = TestChannel(buffering='line')

    def feed(self, data):
        self._chan.put(data)
