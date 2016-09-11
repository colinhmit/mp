# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""

from sys import argv
import json
from stream.twitch_stream import *
from stream.config.universal_config import *
import socket, threading
import zerorpc
import logging

logging.basicConfig()

class StreamServer:

    def __init__(self, config):

        #self.config must be set before calling create_socket!
        self.config = config
        self.init_socket()

        self.streams = {}
        self.threads = {}

    #for python client testing
    def init_socket(self):
        if self.config['mode'] == 'python':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            sock.bind((self.config['host'], self.config['port']))
            sock.listen(self.config['listeners'])
            self.socket = sock

    #stream control
    def create_stream(self, stream):
        self.threads[stream] = threading.Thread(target=self.add_stream, args=(stream,))
        self.threads[stream].start()

    def add_stream(self, stream):
        self.streams[stream] = TwitchStream(twitch_config,stream)
        self.streams[stream].run()

    #js invoked stream call
    def get_stream_trending(self, stream):
        if stream in self.streams.keys():
            if self.config['debug']:
                pp('Found stream!')
            return self.streams[stream].get_trending()

        else:
            if self.config['debug']:
                pp('Stream not found.')
            self.create_stream(stream)
            stream_exists = False

            while not stream_exists:
                stream_exists = stream in self.streams.keys()

            if self.config['debug']:
                pp('Stream created!')

            return self.streams[stream].get_trending()

    #python client testing
    #////////////////////
    def check_for_roger(self, data):
        if data[:5] == 'roger':
            return True

    def check_for_stream(self, data):
       if data[:6] == 'stream':
            return True

    def get_stream(self, data):
        return data[7:]

    def roger(self, message):
        return "roger" + message

    def listen_to_client(self, client_sock, client_address):
        config = self.config
        connected = True
        while connected:
            data = client_sock.recv(config['socket_buffer_size']).rstrip()

            if len(data) == 0:
                pp(('Connection lost by: ' + str(client_address)))
                connected = False

            if config['debug']:
                pp(data)

            if self.check_for_roger(data):
                client_sock.send('Roger')

            if self.check_for_stream(data):

                stream_id = self.get_stream(data)

                if stream_id in self.streams.keys():
                    if config['debug']:
                        pp('Found stream!')

                    #output = json.dumps(self.streams[stream_id].get_chat())
                    output = json.dumps(self.streams[stream_id].get_trending())

                    if config['debug']:
                        pp('Sending: '+ output+config['end_of_data'])

                    client_sock.sendall(output+config['end_of_data'])

                else:
                    if config['debug']:
                        pp('Stream not found.')
                    self.create_stream(stream_id)

                    stream_exists = False
                    while not stream_exists:
                        stream_exists = stream_id in self.streams.keys()

                    if config['debug']:
                        pp('Stream created!')

                    #output = json.dumps(self.streams[stream_id].get_chat())
                    output = json.dumps(self.streams[stream_id].get_trending())
                    if config['debug']:
                        pp('Sending: '+ output+config['end_of_data'])

                    client_sock.sendall(output+config['end_of_data'])

    def run(self):
        sock = self.socket
        config = self.config
        pp(('Server initialized'))

        while True:
            (client_sock, client_address) = sock.accept()
            pp(('Connection initiated by: ' + str(client_address)))
            client_sock.settimeout(60)
            threading.Thread(target = self.listen_to_client,args = (client_sock,client_address)).start()
    #////////////////////

if __name__ == '__main__':
    server = StreamServer(server_config)
    s = zerorpc.Server(server)
    s.bind('tcp://0.0.0.0:4242')
    s.run()

