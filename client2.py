# -*- coding: utf-8 -*-
# client

import socket
import struct
import json
import time

def rpc(sock, in_, params):
    request = json.dumps({"in": in_, "params": params})
    length_prefix = struct.pack("I", len(request)) # 将信息长度（一个数字）编码成 4 个字节的字符串
    sock.sendall(length_prefix)
    sock.sendall(request)
    length_prefix = sock.recv(4)
    length, = struct.unpack("I", length_prefix)
    body = sock.recv(length)
    response = json.loads(body)
    return response["out"], response["result"]

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 8080))
    for i in range(10):
        out, result = rpc(s, "ping", "ireader %d" % i)
        print out, result
        time.sleep(1)
    s.close()
