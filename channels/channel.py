import fcntl
import os

from abc import ABCMeta, abstractmethod


class EndpointClosedException(Exception):
    pass


class Channel(metaclass=ABCMeta):

    def __init__(self, *, buffering='bytes'):
        self._buffer = b''
        self._lf = 0

        self._buffering = buffering
        if buffering == 'line':
            self.read = self._readline
        else:
            self.read = self._read

    @property
    def buffering(self):
        return self._buffering

    @abstractmethod
    def _read(self): #pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def write(self, *data): #pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def close(self): #pragma: no cover
        raise NotImplementedError

    def get_fd(self): #pragma: no cover
        raise NotImplementedError

    def _read_into_buffer(self):
        new_bytes = self._read()
        self._lf = new_bytes.find(b'\n')+1
        if self._lf:
            self._lf += len(self._buffer)
        self._buffer += new_bytes

    def _get_first_line(self):
        result, self._buffer = self._buffer[:self._lf], self._buffer[self._lf:]
        self._lf = self._buffer.find(b'\n')+1
        return result

    def _readline(self):
        if self._lf:
            return self._get_first_line()

        try:
            self._read_into_buffer()
        except EndpointClosedException:
            if not self._buffer:
                raise

        if self._lf:
            return self._get_first_line()

        try:
            self._read_into_buffer()
        except EndpointClosedException:
            result, self._buffer = self._buffer, b''
            return result
        return b''


class PipeChannel(Channel):

    _in = None
    _out = None

    def __init__(self, faucet=None, sink=None, **kwargs):
        super().__init__(**kwargs)
        if faucet is not None:
            fl = fcntl.fcntl(faucet, fcntl.F_GETFL)
            fcntl.fcntl(faucet, fcntl.F_SETFL, fl | os.O_NONBLOCK)
            self._in = os.fdopen(faucet, mode='rb', buffering=0)
        if sink is not None:
            self._out = os.fdopen(sink, mode='wb', buffering=0)

    def _read(self):
        try:
            result = self._in.read()
            if result is None:
                return b''
            if not result:
                raise EndpointClosedException()
            return result
        except (ValueError, OSError) as ex:
            raise EndpointClosedException(ex)

    def write(self, *data):
        try:
            for d in data:
                self._out.write(d)
            self._out.flush()
        except (ValueError, OSError) as ex:
            raise EndpointClosedException(ex)

    def close(self):
        if self._in is not None:
            self._in.close()
        if self._out is not None:
            self._out.close()

    def get_fd(self):
        if self._in is not None:
            return self._in.fileno()
        return super().get_fd()


class SocketChannel(Channel):

    def __init__(self, sock, **kwargs):
        super().__init__(**kwargs)
        self._sock = sock
        self._sock.setblocking(False)

    def _read(self):
        try:
            result = self._sock.recv(4096)
            if not result:
                raise EndpointClosedException()
            return result
        except BlockingIOError:
            return b''
        except OSError as ex:
            raise EndpointClosedException(ex)

    def write(self, *data):
        try:
            for d in data:
                self._sock.send(d)
        except OSError as ex:
            raise EndpointClosedException(ex)

    def close(self):
        self._sock.close()

    def get_fd(self):
        return self._sock.fileno()
