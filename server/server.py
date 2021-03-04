#!/usr/bin/env python3

import threading
import socket
import argparse
import os
import re
import sys

class User:
    def __init__(self,name,addr):
        self.name = name
        self.addr = addr

class Server(threading.Thread):

    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port
    
    """
    Override Thread method run()
    """
    def run(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))

        sock.listen(1)
        print('Listening:', sock.getsockname())

        while True:
            sc, sockname = sock.accept()
            print('Accepted a new connection from {} to {}'.format(sc.getpeername(), sc.getsockname()))

            # New thread for socket
            server_socket = ServerSocket(sc, sockname, self)
            server_socket.start()
            self.connections.append(server_socket)
            print('Ready to receive messages from', sc.getpeername())

    def broadcast(self, message, source):
        for connection in self.connections:
            #Ignore source socket
            if connection.sockname != source:
                connection.send(message)
                

    def remove_connection(self, connection):
        self.connections.remove(connection)


class ServerSocket(threading.Thread):

    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server
        
    """
    Override Thread method run()
    """
    def run(self):

        while True:
            message = self.sc.recv(1024).decode('ascii')
            if message:
                print('{}: {!r}'.format(self.sockname, message))
                self.server.broadcast(message, self.sockname)
            else:
                # Client closed so exit thread and close connection
                print('{} has closed the connection'.format(self.sockname))
                self.sc.close()
                server.remove_connection(self)
                return
    
    def send(self, message):
        self.sc.sendall(message.encode('ascii'))



def exitHandler(server):
    while True:
        userInput = input('')
        if userInput == 'q':
            print('Closing connections')
            for connection in server.connections:
                connection.sc.close()
            print('Server Closing')
            os._exit(0)


if __name__ == '__main__':
    
    if len(sys.argv) != 3:  
        print ("Usage: script, IP address, port number") 
        exit()

    # Create and start server thread
    server = Server(str(sys.argv[1]),int(sys.argv[2]))
    server.start()

    mainLoop = threading.Thread(target = exitHandler, args = (server,))
    mainLoop.start()