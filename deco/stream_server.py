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
import logging
import sys


logging.basicConfig()

class StreamServer:

    def __init__(self, config):

        #self.config must be set before calling create_socket!
        self.config = config
        self.init_socket()

        self.streams = {}
        self.threads = {}
        self.ports = {}
        self.nextPort = self.config['init_port']

    def init_socket(self):
        # if self.config['mode'] == 'python':
        #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #     sock.bind((self.config['host'], self.config['port']))
        #     sock.listen(self.config['listeners'])
        #     self.socket = sock

        ## if self.config['mode'] == 'sqs':
        ##     session = boto3.Session(
        ##         aws_access_key_id='AKIAJJYQ67ESV5S4YVHQ',
        ##         aws_secret_access_key='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',
        ##         region_name='us-west-2',
        ##     )
        ##     self.client = session.client('sqs')

        if self.config['mode'] == 'multicast':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            sock.bind((self.config['host'], self.config['listen_port']))
            sock.listen(self.config['listeners'])
            self.listen_socket = sock

            multisock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            multisock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.config['ttl'])
            self.multi_socket = multisock


    #stream control
    def create_stream(self, stream):
        self.threads[stream] = threading.Thread(target=self.add_stream, args=(stream,))
        self.threads[stream].start()

    def add_stream(self, stream):
        self.streams[stream] = TwitchStream(twitch_config,stream)

        self.ports[stream] = self.nextPort
        self.nextPort += 1

        self.streams[stream].run()

    def check_for_stream(self, data):
       if data[:6] == 'stream':
            return True

    def get_stream(self, data):
        return data[7:]




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

            if self.check_for_stream(data):

                stream_id = self.get_stream(data)

                if stream_id in self.streams.keys():
                    if config['debug']:
                        pp('Found stream!')

                    output = json.dumps(self.ports[stream_id])

                    if config['debug']:
                        pp('Sending: '+ output)

                    client_sock.sendall(output)
                else:
                    if config['debug']:
                        pp('Stream not found.')

                    self.create_stream(stream_id)

                    stream_exists = False
                    while not stream_exists:
                        stream_exists = stream_id in self.streams.keys()

                    if config['debug']:
                        pp('Stream created!')

                    output = json.dumps(self.ports[stream_id])

                    if config['debug']:
                        pp('Sending: '+ output)

                    client_sock.sendall(output)


    def listen(self):
        sock = self.listen_socket
        config = self.config
        pp('Now listening...')
        self.listening = True

        while self.listening:
            (client_sock, client_address) = sock.accept()
            pp(('Connection initiated by: ' + str(client_address)))
            client_sock.settimeout(60)
            threading.Thread(target = self.listen_to_client,args = (client_sock,client_address)).start()

    def multicast(self):
        multisock = self.multi_socket
        config = self.config
        pp('Now multicasting...')
        self.multicast = True

        while self.multicast:
            if len(self.streams.keys()) > 0:
                for stream_key in self.streams.keys():
                    stream_dict = json.dumps(self.streams[stream_key].get_trending())
                    if self.config['debug']:
                        pp(stream_dict)
                    multisock.sendto(stream_dict, (self.config['multicast_server'],self.ports[stream_key]))
            else:
                pass

            time.sleep(0.5)

if __name__ == '__main__':
    server = StreamServer(server_config)

    listen_thread = threading.Thread(target = server.listen).start()
    multicast_thread = threading.Thread(target = server.multicast).start()