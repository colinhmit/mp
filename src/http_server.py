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

class WebServer(Resource):

    isLeaf = True
    stream_client = None
    
    #server protocol
    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        output = self.handle_GET(request.path, request.args)
        return output

    #get control
    def handle_GET(self, path, args):
        if path[0:7] == '/stream':
            return self.stream_client.get_agg_streams(args)
        elif path[0:8] == '/cpanel/':
            if path[8:14] == 'twitch':
                return self.stream_client.handle_cpanel('twitch',args)
            elif path[8:15] == 'twitter':
                return self.stream_client.handle_cpanel('twitter',args)
            else:
                return json.dumps('Invalid path! Valid paths: /cpanel/twitch and /cpanel/twitter')
        elif path[0:10] == '/featured/':
            if path[10:16] == 'twitch':
                return self.stream_client.get_featured('twitch', args)
            elif path[10:17] == 'twitter':
                return self.stream_client.get_featured('twitter', args)
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

        request_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        request_sock.connect((config['request_host'], config['request_port']))
        self.request_sock = request_sock

        data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        data_sock.connect((config['data_host'], config['data_port']))
        self.data_sock = data_sock

    #cpanel response
    def handle_cpanel(self, src, args):
        request = {}
        request[src] = {}

        if 'add' in args.keys():
            request[src]['add'] = args['add'][0].split(',')

        if 'delete' in args.keys():
            request[src]['delete'] = args['delete'][0].split(',')
        
        if 'target_add' in args.keys():
            request[src]['target_add'] = args['target_add'][0].split(',')

        if 'action' in args.keys():
            for action in args['action'][0].split(','):
                if action == 'show':
                    pass
                elif action == 'refresh':
                    request[src]['refresh'] = True
                elif action == 'reset':
                    request[src]['reset'] = True
                else:
                    pass

        self.request_sock.send(json.dumps(request))

        output = []
        if src == 'twitch':
            output = self.twitch_streams.keys()
        elif src == 'twitter':
            output = self.twitter_streams.keys()
        return json.dumps(output)

    def request_stream(self, stream, src):
        request = {}
        request[src] = {'add':[stream]}

        self.request_sock.send(json.dumps(request))

    def get_agg_streams(self, args):
        config = self.config
        trend_dicts = []

        if ('twitch' in args.keys()) and (len(args['twitch'][0])>0):
            for stream_id in args['twitch'][0].split(','):
                if stream_id not in self.twitch_streams.keys():
                    self.twitch_streams[stream_id] = {}
                    self.request_stream(stream_id,'twitch')

                trend_dicts.append(self.twitch_streams[stream_id])

        if ('twitter' in args.keys()) and (len(args['twitter'][0])>0):
            for stream_id in args['twitter'][0].split(','):
                if stream_id not in self.twitter_streams.keys():
                    self.twitter_streams[stream_id] = {}
                    self.request_stream(stream_id,'twitter')

                trend_dicts.append(self.twitter_streams[stream_id])
        
        output = {}
        [output.update(d) for d in trend_dicts]

        if ('filter' in args.keys()) and (len(args['filter'][0])>0):
            for keyword in args['filter'][0].split(','):
                for msg in output.keys():
                    if keyword.lower() in msg.lower():
                        del output[msg]

        return json.dumps(output)

    def get_featured(self, src, args):
        output = []

        if src == 'twitch':
            output = self.twitch_featured
        elif src == 'twitter':
            output = self.twitter_featured

        if ('limit' in args.keys()) and (len(args['limit'][0])>0):
            limit = int(args['limit'][0])
            output = output[0:limit]

        return json.dumps(output)

    def recv_data(self):
        sock = self.data_sock
        config = self.config
        self.recv = True


        while self.recv:
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
                        total_data[-2]=last_pair[:last_pair.find(config['end_of_data'])]
                        total_data.pop()
                        break

            jsondata = json.loads(''.join(total_data))
            self.twitch_streams = jsondata['twitch_streams']
            self.twitter_streams = jsondata['twitter_streams']

            self.twitch_featured = jsondata['twitch_featured']
            self.twitter_featured = jsondata['twitter_featured']

    def run(self):
        pp('Initializing Web Server...')
        resource = WebServer()
        resource.stream_client = self

        factory = Site(resource)
        #prod aws
        #reactor.listenTCP(self.config['port'], factory)

        #local testing
        reactor.listenTCP(4808, factory)

        pp('Starting Web Server...')
        reactor.run()

if __name__ == '__main__':
    #init
    client = StreamClient(client_config)
    recv_thread = threading.Thread(target = client.recv_data).start()
    client.run()
