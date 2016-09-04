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
            sock.send('roger')
        except:
            pp('Cannot connect to server (%s:%s).' % (server, self.config['port']), 'error')
            sys.exit()        
        
        sock.settimeout(None)
                
        if self.check_for_Roger(sock.recv(1024)):
            pp('Connection successful.')
        else:
            pp('Connection unsuccessful.', 'error')
            sys.exit()
        
        self.socket = sock
    
    def check_for_Roger(self, data):
        if data[:5] == 'Roger': 
            return True
    
    def get_from_stream(self, stream):
        sock = self.socket
        config = self.config

        sock.send('stream:' + stream)   
   
        total_data=[];data=''
        
        while True:
                data = sock.recv(config['socket_buffer_size']).rstrip()
                if config['end_of_data'] in data:
                    total_data.append(data[:data.find(config['end_of_data'])])
                    break
                total_data.append(data)
                if len(total_data)>1:
                    #check if end_of_data was split
                    last_pair=total_data[-2]+total_data[-1]
                    if config['end_of_data'] in last_pair:
                        total_data[-2]=last_pair[:last_pair.find(End)]
                        total_data.pop()
                        break
        return json.loads(''.join(total_data))
        
#        
if __name__ == '__main__':
    pp('Initializing Client...')
    server = raw_input('Enter the host: ')
    client = StreamClient(client_config)
    client.connect_to_server(server)
    
    if client_config['mode'] == 'demo':
        stream = raw_input('Enter the stream ID: ')
        while True:
            #pp('# messages received: '+str(len(client.get_from_stream(stream))))
            pp("****************************")
            trending = client.get_from_stream(stream)
            for key in trending.keys():
                pp(key+" : "+str(trending[key][0]))
            pp("****************************")
            time.sleep(5)