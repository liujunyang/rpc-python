# -*- coding: utf-8 -*-

import struct
import json
import socket
import asyncore
from cStringIO import StringIO

class RPCHandler(asyncore.dispatcher_with_send):
    def __init__(self, sock, addr):
        asyncore.dispatcher_with_send.__init__(self, sock = sock)
        self.addr = addr
        self.handlers = {
            "ping": self.ping
        }
        self.rbuf = StringIO()

    def handle_connect(self):
        print self.addr, "comes"

    def handle_close(self):
        print self.addr, "bye"
        self.close()

    def handle_read(self):
        while True:
            content = self.recv(1024)
            if content:
                self.rbuf.write(content)
            if len(content) < 1024:
                break
        self.handle_rpc()

    def handle_rpc(self):
        while True:
            self.rbuf.seek(0)
            length_prefix = self.rbuf.read(4)
            if len(length_prefix) < 4: # 这里还没有解码，在后面unpack，如果这里都不够4个字节，也就是连信息长度都没发全
                break
            length, = struct.unpack("I", length_prefix)
            body = self.rbuf.read(length)
            if len(body) < length: # 不足一个消息
                break
            request = json.loads(body)
            in_ = request['in']
            params = request['params']
            print in_, params
            handler = self.handlers[in_]
            handler(params)
            left = self.rbuf.getvalue()[length + 4:] # 切片，缓冲区截断，旧缓冲区扔掉
            self.rbuf = StringIO()
            self.rbuf.write(left)
        self.rbuf.seek(0, 2) # 将游标挪到末尾，以便后面的内容直接追加

    def ping(self, params):
        self.send_result('pong', params)

    def send_result(self, out, result):
        response = {"out": out, "result": result}
        body = json.dumps(response)
        length_prefix = struct.pack("I", len(body))
        self.send(length_prefix)
        self.send(body)


class RPCServer(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(1)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            RPCHandler(sock, addr)

if __name__ == "__main__":
    RPCServer("localhost", 8080)
    asyncore.loop()

