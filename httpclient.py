#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data[0].split(' ')[1]
        print("Code: "+code)
        return int(code)

    def get_headers(self,data):
        return data.split("\r\n")

    def get_body(self, data):
        return data.split("\r\n")[-1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        return self.recvall(self.socket)
        
    def close(self):
        self.socket.close()

    def get_path(self, line):
        if line.path:
            paths = line.path
        else:
            paths = '/'
        return paths

    def get_line_and_port(self, url):
        line = urllib.parse.urlparse(url)
        if line.port:
            ports = line.port
        else:
            ports = 80
        return line,ports

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        lines,ports = self.get_line_and_port(url)

        hs = lines.hostname
        self.connect(hs,ports)
        
        paths = self.get_path(lines)

        message = "GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\nConnection: close\r\n\r\n".format(path=paths, host=hs)
        body = self.sendall(message)
        header = self.get_headers(body)
        code = self.get_code(header)
        print(body)
        self.close()
        return HTTPResponse(code, body)
    
    def POST(self, url, args=None):
        body = ""
        lines,ports = self.get_line_and_port(url)

        hs = lines.hostname
        self.connect(socket.gethostbyname(hs),ports)

        if args != None:
            body = urllib.parse.urlencode(args)

        paths = self.get_path(lines)

        message = "POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {length}\r\n\r\n{data}\r\n\r\nConnection: close\r\n\r\n".format(path=paths,data=body,length=len(body),host=hs)
        self.connect(hs,ports)
        data = self.sendall(message)
        header = self.get_headers(data)
        code = self.get_code(header)
        bodies = self.get_body(data)
        print(data)
        self.close()
        return HTTPResponse(code, bodies)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
