#!/usr/bin/env python
# coding: utf8

import socket
import thread
import sys

# local class
from log import Log

MAX_PACKET = 32768
HOST = '0.0.0.0'
PORT = 60600
LISTEM = 1
MAX_THREAD = 5


def recv_all(sock):
    r'''Receive everything from `sock`, until timeout occurs, meaning sender
    is exhausted, return result as string.'''

    # dirty hack to simplify this stuff - you should really use zero timeout,
    # deal with async socket and implement finite automata to handle incoming data

    prev_timeout = sock.gettimeout()
    try:
        sock.settimeout(0.01)

        rdata = []
        while True:
            try:
                rdata.append(sock.recv(MAX_PACKET))
            except socket.timeout:
                return ''.join(rdata)

        # unreachable
    finally:
        sock.settimeout(prev_timeout)


def normalize_line_endings(s):
    r'''Convert string containing various line endings like \n, \r or \r\n,
    to uniform \n.'''

    return ''.join((line + '\n') for line in s.splitlines())


def run():

    Log('starting up webserver')

    # Create TCP socket listening on 10000 port for all connections,
    # with connection queue of length 1
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM,
                                socket.IPPROTO_TCP)
    server_sock.bind((HOST, PORT))
    server_sock.listen(LISTEM)

    threads = 0

    while True:

        Log("waiting for a connections")

        client_sock, client_addr = server_sock.accept()

        Log('new connection accept')

        thread.start_new_thread(on_new_client, (client_sock,))

    server_sock.close()


def on_new_client(client_sock):

    while True:

        # headers and body are divided with \n\n (or \r\n\r\n - that's why we
        # normalize endings). In real application usage, you should handle
        # all variations of line endings not to screw request body
        request = normalize_line_endings(recv_all(client_sock))  # hack again
        request_head, request_body = request.split('\n\n', 1)

        # first line is request headline, and others are headers
        request_head = request_head.splitlines()
        request_headline = request_head[0]
        # headers have their name up to first ': '. In real world uses, they
        # could duplicate, and dict drops duplicates by default, so
        # be aware of this.
        request_headers = dict(x.split(': ', 1) for x in request_head[1:])

        # headline has form of "POST /can/i/haz/requests HTTP/1.0"
        request_method, request_uri, request_proto = request_headline.split(
            ' ', 3)

        Log('request body: ' + request_body)

        response_body = ["Hello!!!"]
        response_body_raw = ''.join(response_body)

        # Clearly state that connection will be closed after this response,
        # and specify length of response body
        response_headers = {
            'Content-Type': 'application/json; encoding=utf8',
            'Content-Length': len(response_body_raw),
            'Connection': 'close',
        }

        response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in
                                       response_headers.iteritems())

        # Reply as HTTP/1.1 server, saying "HTTP OK" (code 200).
        response_proto = 'HTTP/1.1'
        response_status = '200'
        response_status_text = 'OK'  # this can be random

        # sending all this stuff
        client_sock.send('%s %s %s' % (response_proto, response_status,
                                       response_status_text))
        client_sock.send(response_headers_raw)
        client_sock.send('\n')  # to separate headers from body
        client_sock.send(response_body_raw)

        # and closing connection, as we stated before
        Log('connection close')
        client_sock.close()
        thread.exit()


Log("start script webserver")

try:
    run()
except IOError as (errno, strerror):
    Log("I/O error({0}): {1}".format(errno, strerror), "ERROR")
except Exception as e:
    Log(str(e), "ERROR")
