import sys
import threading
import socket
import argparse
import os
import re

class Send(threading.Thread):

    def __init__(self, sock,user):
        super().__init__()
        self.sock = sock
        self.user = user

    def run(self):

        while True:
            message = input('{}: '.format(self.user.name))
            #Few basic commands.
            if message == '/quit':
                self.sock.sendall('#channel={} {} has left {}.'.format(self.user.channel,self.user.name,self.user.channel).encode('ascii'))
                break
            elif '/join' in message:
                match = re.search(r'(?<=/join )[^.\s]*',message)
                if match:
                    foundChannel = match.group(0)
                    if foundChannel:
                        self.user.channel = foundChannel
                        print('joined {}'.format(self.user.channel))
                        self.sock.sendall('#channel={} {} has landed {}'.format(self.user.channel,self.user.name, self.user.channel).encode('ascii'))
            elif '/whisper' in message:            
                match = re.search(r'(?<=/whisper )[^.\s]*',message)
                if match:
                    whisperTarget = match.group(0)
                    message.replace('/whisper {}'.format(whisperTarget), '')
                    self.sock.sendall('#whisper={} {}: {}'.format(whisperTarget, self.user.name, message).encode('ascii'))

            #Normal message
            else:
                self.sock.sendall('#channel={} {}: {}'.format(self.user.channel, self.user.name, message).encode('ascii'))

        print('\nLeaving')
        self.sock.close()
        os._exit(0)

class Receive(threading.Thread):

    def __init__(self, sock, user):
        super().__init__()
        self.sock = sock
        self.user = user

    def run(self):
        while True:
            message = self.sock.recv(1024)
            if message:
                if "#channel=" in message.decode('ascii'):
                    match = re.search(r'(?<=#channel=)[^.\s]*',message.decode('ascii'))
                    if match:
                        foundChannel = match.group(0)
                        if foundChannel in self.user.channel:
                            print('\r{}\n{}: '.format(message.decode('ascii').replace("#channel={} "
                            .format(foundChannel),""), self.user.name), end = '')
                if "#whisper=" in message.decode('ascii'):
                    match = re.search(r'(?<=#whisper=)[^.\s]*',message.decode('ascii'))
                    if match:
                        name = match.group(0)
                        if name == self.user.name:
                            print('\r{}\n{}: '.format(message.decode('ascii').replace("#whisper={} ".format(name),">")
                            .replace("/whisper {}".format(name),""), self.user.name), end = '')
            else:
                print('\nConnection to server lost')
                self.sock.close()
                os._exit(0)

class User:
    def __init__(self, name, channel):
        self.name = name
        self.channel = channel
    

class Client:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    
    def start(self):
        print('Connecting to {}:{}...'.format(self.host, self.port))
        self.sock.connect((self.host, self.port))
        print('Connected to {}:{}'.format(self.host, self.port))

        print()
        name = input('Name: ')
        print()
        channel = 'general'

        user = User(name,channel)

        print()
        print('Hi, {}! joining {}'.format(name,channel))

        # New threads for receicing and sending
        send = Send(self.sock, user)
        receive = Receive(self.sock, user)

        send.start()
        receive.start()

        self.sock.sendall('#channel={} {} has landed {}'.format(channel, name, channel).encode('ascii'))

        print('\rto leave type "/quit"\n')
        print('\rto join channel type "/join channelname"\n')
        print('{}: '.format(name), end = '')

if __name__ == '__main__':

    if len(sys.argv) != 3:  
        print ("Correct usage: script, IP address, port number") 
        exit()

    client = Client(str(sys.argv[1]),int(sys.argv[2]))
    client.start()