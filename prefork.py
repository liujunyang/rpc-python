# -*- coding: utf-8 -*-

import os
import struct
import json
import socket

def handle_conn(conn, addr, handlers):
    print addr, "comes"
    while True:
        length_prefix = conn.recv(4)
        if not length_prefix:
            print addr, "bye"
            conn.close()
            break
        length, = struct.unpack("I", length_prefix)
        body = conn.recv(length)
        request = json.loads(body)
        in_ = request["in"]
        params = request["params"]
        print in_, params
        handler = handlers[in_]
        handler(conn, params)

def loop(sock, handlers):
    while True:
        conn, addr = sock.accept()
        handle_conn(conn, addr, handlers)

def ping(conn, params):
    send_result(conn, "pong", params)

def send_result(conn, out, result):
    response = json.dumps({"out": out, "result": result})
    length_prefix = struct.pack("I", len(response))
    conn.sendall(length_prefix)
    conn.sendall(response)

def prefork(n):
    for i in range(n):
        pid = os.fork()
        if pid < 0:
            return
        if pid > 0:
            continue
        if pid == 0:
            break

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', 8080))
    sock.listen(1)
    prefork(10)
    handlers = {
        "ping": ping
    }
    loop(sock, handlers)
