# Channels [![Build Status](https://travis-ci.com/aragaer/channels.svg?branch=master)](https://travis-ci.com/aragaer/channels) [![codecov](https://codecov.io/gh/aragaer/channels/branch/master/graph/badge.svg)](https://codecov.io/gh/aragaer/channels) [![BCH compliance](https://bettercodehub.com/edge/badge/aragaer/channels?branch=master)](https://bettercodehub.com/results/aragaer/channels) [![donate using paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=aragaer@gmail.com&lc=RU&item_name=CHANNELS&currency_code=USD&bn=PP-DonationsBF:btn_donate_SM.gif:NonHosted)

Simple wrapper around file objects and sockets that provides uniform
interface to both.

Example:

    pipe_chan = PipeChannel(sys.stdin.fileno(), sys.stdout.fileno())
	sock_chan = SocketChannel(socket.create_connection(('127.0.0.1', 8080))

## Classes

### Channel
Channel is the base class for different channels. Every channel
implements the following methods:

`read(self)`

Performs a non-blocking read and returns any bytes available. Raises
`EndpointClosedException` if the channel is closed.

`write(self, *data)`

Writes chunks of bytes to the channel. Raises `EndpointClosedException`.

`close(self)`

Closes the channel and frees up the resources.

`get_fd(self)`

Returns a file descriptor number that can be used for `poll` or
`epoll` for reading. Raises `NotImplementedError` if (custom) channel
doesn't support reading.

Every channel has a `buffering` property (read-only). It is equal to
`'line'` for line-buffered channels. It should be `'bytes'` otherwise
but any value other than `'line'` works.

The following channel classes are implemented:

### PipeChannel

`PipeChannel(faucet=None, sink=None, *, buffering='bytes')`

`faucet` should be a file descriptor open for reading. `sink` should
be a file descriptor open for writing. If both are provided, the
channel is bi-directional. Sets `faucet` to non-blocking mode.

If `buffering` is set to `'line'` the channel uses line-buffering for
reading. Every `read` call will return `b''` if there is no complete
line available even if there is any data at all. If channel is closed
but there is data in buffer, calls to `read` will return lines from
buffer until it is exhausted. Last line maybe an incomplete line (no
`'\n'` in the end).

### SocketChannel

`SocketChannel(sock, *, buffering='bytes')`

Wraps a socket for non-blocking IO. See PipeChannel for more info on
`buffering` parameter.

### TestChannel

(in package channels.testing)

`TestChannel(*, buffering='bytes')`

See PipeChannel for more info on `buffering` parameter.

Provides `put` and `get` methods to to feed data to `read` and fetch
"written" data respectively.

### Poller
Poller is a wrapper for `select.poll` that also supports accepting and
keeping track of TCP/Unix clients.

`Poller(*, buffering='bytes')`

Creates a poller object. All accepted client channels inherit the
`buffering` parameter.

`register(self, channel)`

Registers the channel for polling.

`add_server(self, sock)`

Registers a server socket. Poller will accept incoming connections and
automatically register clients.

`unregister(self, channel)`

Removes a registered channel.

`close_all(self)`

Closes all registered channels and servers.

`poll(self, timeout=None)`

Performs a single call to `select.poll()`. `timeout` is the number of
seconds for polling or `None` for infinite polling. Return value is a
list of pairs in format of `(data, channel)` for channels and `((addr,
client_channel), sock)` for server sockets. `addr` depends on socket
type. For line-based channels single `poll` call will return one
result for every line available.
