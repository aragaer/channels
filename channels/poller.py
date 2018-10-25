import logging
import select
import time

from .channel import EndpointClosedException, SocketChannel


_LOGGER = logging.getLogger(__name__)


class Poller:

    def __init__(self, *, buffering='bytes'):
        self._servers = {}
        self._channels = {}
        self._poll = select.poll()
        self._buffering = buffering

    @staticmethod
    def _readlines(channel):
        result = []
        while True:
            data = channel.read()
            if not data:
                return result
            result.append(data)

    def poll(self, timeout=None):
        if timeout is not None:
            timeout = timeout * 1000
        result = []
        for fd, event in self._poll.poll(timeout):
            if fd in self._channels:
                channel = self._channels[fd]
                try:
                    if channel.buffering == 'line':
                        result.extend([(data, channel)
                                       for data in self._readlines(channel)])
                    else:
                        result.append((channel.read(), channel))
                except EndpointClosedException:
                    result.append((b'', channel))
            else:
                server = self._servers[fd]
                sock, addr = server.accept()
                client = SocketChannel(sock, buffering=self._buffering)
                self.register(client)
                result.append(((addr, client), server))
        return result

    def register(self, channel):
        fd = channel.get_fd()
        self._channels[fd] = channel
        self._poll.register(fd, select.POLLIN)
        _LOGGER.debug("Registered channel %s with fd %d", channel, fd)

    def add_server(self, server):
        self._servers[server.fileno()] = server
        self._poll.register(server.fileno())

    def close_all(self):
        for channel in self._channels.values():
            channel.close()
        for server in self._servers.values():
            server.close()

    def unregister(self, channel):
        fd = channel.get_fd()
        self._poll.unregister(fd)
        del self._channels[fd]
        _LOGGER.debug("Unregistered channel %s with fd %d", channel, fd)
