#!/usr/bin/env python
import socket
import selectors
import types
import sys

messages = [b'Message 1 from client.',
            b'Message 2 from client.']

sel = selectors.DefaultSelector()

#
# host = str(sys.argv[1])
# port = int(sys.argv[2])
# num_conns = int(sys.argv[3])

host = '127.0.0.1'
port = 65432
num_conns = 2


def start_connection(host, port, num_conns):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print('starting connection', connid, 'to', server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(connid=connid,
                                     msg_total=sum(len(m) for m in messages),
                                     recv_total=0,
                                     messages=list(messages),
                                     outb=b'')
        sel.register(sock, events, data=data)


def service_connectino(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print('received', repr(recv_data), 'from connection', data.connid)
        if not recv_data or data.recv_total == data.msg_total:
            print('closing connection', data.connid)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print('sending', repr(data), 'to connection', data.connid)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


start_connection(host, port, num_conns)