# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 21:28:46 2016

@author: colinh
"""

import json, sys,time
from stream.twitch_stream import *
from stream.config.universal_config import *
import socket


class StreamClient:

    def __init__(self, config):
        #self.config must be set before calling create_socket!
        self.config = config
        
    def connect_to_server(self, server=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        if server == None:
            server = self.config['default_server']
        
        try:
            sock.connect((server, self.config['port']))
        except:
            pp('Cannot connect to server (%s:%s).' % (server, self.config['port']), 'error')
            sys.exit()        
        
        sock.settimeout(None)
        
        self.socket = sock
    
    def connect_to_multicast(self, port):
        multicast_group = self.config['multicast_server']
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except AttributeError:
             pass
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, self.config['ttl'])
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
        sock.bind((multicast_group, port))
        host = socket.gethostbyname(socket.gethostname())
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
        sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(multicast_group) + socket.inet_aton(host))
        self.multi_socket = sock 

    def get_port(self, stream):
        sock = self.socket
        config = self.config

        sock.send('stream:' + stream)

        data = sock.recv(config['socket_buffer_size']).rstrip()

        return json.loads(data)
        
    def recv_multicast(self):
        sock = self.multi_socket
        config = self.config

        while True:
            pp('starting')
            data, address = sock.recvfrom(65535)
            pp(data)
            pp('done')
            print json.loads(data)

    def single_recv_multicast(self):
        sock = self.multi_socket
        config = self.config
        data, address = sock.recvfrom(65535)
        pp(data)
        
    # def get_from_stream(self, stream):
    #     sock = self.socket
    #     config = self.config

    #     sock.send('stream:' + stream)   
   
    #     total_data=[];data=''
        
    #     while True:
    #             data = sock.recv(config['socket_buffer_size']).rstrip()
    #             if config['end_of_data'] in data:
    #                 total_data.append(data[:data.find(config['end_of_data'])])
    #                 break
    #             total_data.append(data)
    #             if len(total_data)>1:
    #                 #check if end_of_data was split
    #                 last_pair=total_data[-2]+total_data[-1]
    #                 if config['end_of_data'] in last_pair:
    #                     total_data[-2]=last_pair[:last_pair.find(End)]
    #                     total_data.pop()
    #                     break
    #     return json.loads(''.join(total_data))
        
if __name__ == '__main__':
    pp('Initializing Client...')
    server = raw_input('Enter the host: ')
    client = StreamClient(client_config)
    client.connect_to_server(server)
    stream = raw_input('Enter the stream: ')
    port = client.get_port(stream)
    client.connect_to_multicast(port)
    # if client_config['mode'] == 'demo':
    #     stream = raw_input('Enter the stream ID: ')
    #     while True:
    #         #pp('# messages received: '+str(len(client.get_from_stream(stream))))
    #         pp("****************************")
    #         trending = client.get_from_stream(stream)
    #         for key in trending.keys():
    #             pp(key+" : "+str(trending[key][0]))
    #         pp("****************************")
    #         time.sleep(5)