# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""

import socket
import threading
import logging
import sys
import json
import time
import requests
import re

logging.basicConfig()

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site

from streams.twitch_stream import *
from streams.twitter_stream import *
from config.universal_config import *

import streams.utils.twtr as twtr_


client_config = {
    
    # details required to host the server
    'host': '127.0.0.1',
    'multicast_server': '239.192.1.100',
    'multicast_port': 6000,
    'port': 4808,
    'ttl': 32,
    
    # if set to true will display any data received
    'debug': False,

    # if set to true will log all messages from all channels
    # TODO
    'log_messages': False,

    # maximum amount of bytes to receive from socket - 1024-4096 recommended
    'socket_buffer_size': 4096,
 
      'end_of_data': '//data_sent//',
      
      #modes: backtest, demo
      'mode': 'demo'
 
}

class WebServer(Resource):

    isLeaf = True
    stream_server = None
    
    #server protocol
    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        output = self.handle_GET(request.path, request.args)
        return output

    #get control
    def handle_GET(self, path, args):
        if path[0:7] == '/stream':
            return self.stream_server.get_agg_streams(args)
        elif path[0:8] == '/cpanel/':
            if path[8:14] == 'twitch':
                return self.stream_server.handle_cpanel('twitch',args)
            elif path[8:15] == 'twitter':
                return self.stream_server.handle_cpanel('twitter',args)
            else:
                return json.dumps('Invalid path! Valid paths: /cpanel/twitch and /cpanel/twitter')
        elif path[0:10] == '/featured/':
            if path[10:16] == 'twitch':
                return self.stream_server.get_twitch_featured(args)
            elif path[10:17] == 'twitter':
                return self.stream_server.get_twitter_featured(args)
            else:
                return json.dumps('Invalid path! Valid paths: /featured/twitch and /featured/twitter')
        else:
            return json.dumps('Invalid path! Valid paths: /stream and /cpanel/.../')

class StreamClient():
    def __init__(self, config):
        pp('Initializing Stream Client...')
        self.config = config
        self.init_sockets()

        self.twitch_streams = {}
        self.twitter_streams = {}

        self.twitch_featured = []
        self.twitter_featured = []


    def init_sockets(self):
        config = self.config

        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        ####CONFIG
        server_sock.connect((config['host'], config['port']))
        self.server_sock = server_sock

        multi_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            multi_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except AttributeError:
             pass
        multi_sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, self.config['ttl'])
        multi_sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
        multi_sock.bind((config['multicast_server'], config['multicast_port']))
        host = socket.gethostbyname(socket.gethostname())
        multi_sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
        multi_sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(config['multicast_server']) + socket.inet_aton(host))
        self.multi_socket = multi_sock 

    #/////////////////////
    #cpanel response
    def handle_cpanel(self, src, args):
        output = []
        return json.dumps(output)

    def get_agg_streams(self, args):
        config = self.config
        trend_dicts = []

        if ('twitch' in args.keys()) and (len(args['twitch'][0])>0):
            for stream_id in args['twitch'][0].split(','):
                trend_dicts.append(self.twitch_streams[stream_id])

        if ('twitter' in args.keys()) and (len(args['twitter'][0])>0):
            for stream_id in args['twitter'][0].split(','):
                trend_dicts.append(self.twitter_streams[stream_id])
        
        output = {}
        [output.update(d) for d in trend_dicts]

        if ('filter' in args.keys()) and (len(args['filter'][0])>0):
            for keyword in args['filter'][0].split(','):
                for msg in output.keys():
                    if keyword.lower() in msg.lower():
                        del output[msg]

        return json.dumps(output)

    def handle_multicast(self):
        sock = self.multi_socket
        config = self.config

        while True:
            data, address = sock.recvfrom(65535)
            jsondata = json.loads(data)

            self.twitch_streams = jsondata['twitch_streams']
            self.twitter_streams = jsondata['twitter_streams']

            self.twitch_featured = jsondata['twitch_featured']
            self.twitter_featured = jsondata['twitter_featured']
            pp(self.twitch_streams)

if __name__ == '__main__':
    #init
    client = StreamClient(client_config)
    client.server_sock.send(json.dumps({'twitch':{'add':['overwatch_nge']}}))
    multicast_thread = threading.Thread(target = client.handle_multicast).start()
