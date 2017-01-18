# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""

import socket
import threading
import logging
import sys
import struct
import json
import time
import requests
import re
import pickle

logging.basicConfig()

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site

from streams.utils.functions_general import *
from config.universal_config import *

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

        #CJK regex
        self.pattern = re.compile('[^\w\s\'\"!.,$&?:;_-]+')


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

        if 'add' in args:
            request[src]['add'] = [self.pattern.sub('',x).lower() for x in args['add'][0].split(',')]

        if 'delete' in args:
            request[src]['delete'] = [self.pattern.sub('',x).lower() for x in args['delete'][0].split(',')]

        if 'target_add' in args:
            request[src]['target_add'] = [self.pattern.sub('',x).lower() for x in args['target_add'][0].split(',')]

        if 'action' in args:
            for action in args['action'][0].split(','):
                if action == 'show':
                    pass
                elif action == 'refresh':
                    request[src]['refresh'] = True
                elif action == 'reset':
                    request[src]['reset'] = True
                else:
                    pass

        pp('handling cpanel request...')
        pp(request)
        self.request_sock.send(json.dumps(request))
        pp('handle_cpanel request done.')

        output = []
        if src == 'twitch':
            output = self.twitch_streams.keys()
        elif src == 'twitter':
            output = self.twitter_streams.keys()

        pp('returning output')
        pp(output)
        return json.dumps(output)

    def request_stream(self, stream, src):
        request = {}
        request[src] = {'add':[stream]}

        pp('requesting stream...')
        pp(request)
        self.request_sock.send(json.dumps(request))

    def get_agg_streams(self, args):
        config = self.config
        trend_dicts = []

        if ('twitch' in args) and (len(args['twitch'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitch'][0].split(',')]:
                if stream_id not in self.twitch_streams:
                    self.twitch_streams[stream_id] = {}
                    self.request_stream(stream_id,'twitch')

                trend_dicts.append(self.twitch_streams[stream_id])

        if ('twitter' in args) and (len(args['twitter'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitter'][0].split(',')]:
                if stream_id not in self.twitter_streams:
                    self.twitter_streams[stream_id] = {}
                    self.request_stream(stream_id,'twitter')

                trend_dicts.append(self.twitter_streams[stream_id])
        
        output = {}
        [output.update(d) for d in trend_dicts]

        if ('filter' in args) and (len(args['filter'][0])>0):
            for keyword in args['filter'][0].split(','):
                for msg in output:
                    if keyword.lower() in msg.lower():
                        del output[msg]

        try:
            jsonoutput = json.dumps(output)
        except Exception, e:
            pp('json dump output in get_agg_streams failed!')
            pp(output)
            pp('//////end json dump output failed/////')
            jsonoutput = json.dumps({})

        return jsonoutput

    def get_featured(self, src, args):
        output = []

        if src == 'twitch':
            output = self.twitch_featured
        elif src == 'twitter':
            output = self.twitter_featured

        if ('limit' in args) and (len(args['limit'][0])>0):
            limit = int(args['limit'][0])
            output = output[0:limit]

        try:
            jsonoutput = json.dumps(output)
        except Exception, e:
            pp('json dump output in get_featured failed!')
            pp(output)
            pp('//////end json dump output failed/////')
            jsonoutput = json.dumps({})

        return jsonoutput

    def recv_helper(self, bytes):
        sock = self.data_sock
        data = ''
        while len(data) < bytes:
            packet = sock.recv(bytes - len(data))
            if not packet:
                return None
            data += packet
        return data

    def recv_data(self):
        config = self.config
        self.recv = True

        while self.recv:

            raw_len = self.recv_helper(4)
            msg_len = struct.unpack('>I', raw_len)[0]
            # Read the message data
            inc_pickle_data = self.recv_helper(msg_len)

            try:
                pickle_data = pickle.loads(inc_pickle_data)
            except Exception, e:
                pp('json load input in recv_data failed!')
                pp('expected inc_data_len:'+raw_len)
                pp('actual received :' + str(len(inc_pickle_data)))
                pp('//////end json load output failed/////')

            pickle_data = pickle.loads(inc_pickle_data)
            self.twitch_streams = pickle_data['twitch_streams']
            self.twitter_streams = pickle_data['twitter_streams']

            self.twitch_featured = pickle_data['twitch_featured']
            self.twitter_featured = pickle_data['twitter_featured']

    def run(self):
        pp('Initializing Web Server...')
        resource = WebServer()
        resource.stream_client = self

        factory = Site(resource)

        reactor.listenTCP(self.config['port'], factory)

        pp('Starting Web Server...')
        reactor.run()

if __name__ == '__main__':
    #init
    client = StreamClient(client_config)
    recv_thread = threading.Thread(target = client.recv_data).start()
    client.run()
