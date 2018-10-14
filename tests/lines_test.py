import os
import time
import unittest

from channels import Channel, EndpointClosedException, LineChannel, PipeChannel


def _readall(channel):
    for _ in range(100):
        time.sleep(0.001)
        line = channel.read()
        if line is not None:
            return line


class SimpleChannel(Channel):

    _bytes = b''
    _closed = False

    def read(self):
        if self._closed and not self._bytes:
            raise EndpointClosedException
        result, self._bytes = self._bytes, b''
        return result

    def write(self, *data):
        if self._closed:
            raise EndpointClosedException
        self._bytes += b''.join(data)

    def close(self):
        self._closed = True


class LineBufferingTest(unittest.TestCase):

    def setUp(self):
        self._inner = SimpleChannel()
        self._chan = LineChannel(self._inner)

    def test_write_line(self):
        self._chan.write(b'test\n')

        self.assertEqual(self._chan.read(), b'test\n')

    def test_write_partial(self):
        self._chan.write(b'te')

        self.assertEqual(self._chan.read(), b'')

    def test_write_two_step(self):
        self._chan.write(b'te')

        self.assertEqual(self._chan.read(), b'')

        self._chan.write(b'st\n')

        self.assertEqual(self._chan.read(), b'test\n')
        self.assertEqual(self._chan.read(), b'')

    def test_write_more_than_one_line(self):
        self._chan.write(b'a\nb\n')

        self.assertEqual(self._chan.read(), b'a\n')
        self.assertEqual(self._chan.read(), b'b\n')

    def test_read_last_line(self):
        self._chan.write(b'test')

        self._inner.close()

        self.assertEqual(self._chan.read(), b'test')

    def test_read_including_last_line(self):
        self._chan.write(b'hello\nworld')

        self._inner.close()

        self.assertEqual(self._chan.read(), b'hello\n')
        self.assertEqual(self._chan.read(), b'world')
        with self.assertRaises(EndpointClosedException):
            print(self._chan.read())

    def test_get_fd_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self._chan.get_fd()


class LineChannelTest(unittest.TestCase):

    def test_get_fd_readable(self):
        faucet_fd, sink_fd = os.pipe()
        inner = PipeChannel(faucet=faucet_fd)
        channel = LineChannel(inner)

        self.assertEqual(channel.get_fd(), faucet_fd)

    def test_get_fd_write_only(self):
        faucet_fd, sink_fd = os.pipe()
        inner = PipeChannel(sink=sink_fd)
        channel = LineChannel(inner)

        with self.assertRaises(NotImplementedError):
            channel.get_fd()
