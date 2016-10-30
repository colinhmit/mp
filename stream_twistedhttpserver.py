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
import json

logging.basicConfig()

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site

import time

class WebServer(Resource):

    isLeaf = True
    stream_server = None
    
    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        output = self.handle_GET(request.path)
        return output

    #get control
    def handle_GET(self, path):
        #stream request
        if path[0:8] == '/stream/':
            return self.stream_server.get_stream(path[8:])
        else:
            return json.dumps('Invalid path! Valid paths: /stream/')

class StreamServer():

    def __init__(self, config):
        pp('Initializing Stream Server...')
        #self.config must be set before calling create_socket!
        self.config = config
        
        self.streams = {}
        self.threads = {}

    #stream control
    def create_stream(self, stream):
        self.threads[stream] = threading.Thread(target=self.add_stream, args=(stream,))
        self.threads[stream].start()

    def add_stream(self, stream):
        self.streams[stream] = TwitchStream(twitch_config,stream)
        self.streams[stream].run()

    def get_stream(self, stream_id):
        config = self.config

        stream_id = stream_id.lower()
        
        if stream_id in self.streams.keys():
            if config['debug']:
                pp('Found stream!')
        else:
            if config['debug']:
                pp('Stream not found.')

            self.create_stream(stream_id)

            stream_exists = False
            while not stream_exists:
                stream_exists = stream_id in self.streams.keys()

            if config['debug']:
                pp('Stream created!')

        output = json.dumps(self.streams[stream_id].get_trending())

        if config['debug']:
            pp('Sending: '+ output)

        return output

    def filter(self):
        self.filter_loop = True

        while self.filter_loop:
            if len(self.streams.keys()) > 0:
                for stream_key in self.streams.keys():
                    self.streams[stream_key].filter_trending()
            else:
                pass

            time.sleep(0.8)

    def render(self):
        self.clean_loop = True

        while self.clean_loop:
            if len(self.streams.keys()) > 0:
                for stream_key in self.streams.keys():
                    self.streams[stream_key].render_trending()
            else:
                pass

            time.sleep(0.2)

    def run(self):
        pp('Initializing Web Server...')
        resource = WebServer()
        resource.stream_server = self

        factory = Site(resource)
        #prod aws
        #reactor.listenTCP(self.config['port'], factory)
        #local testing
        reactor.listenTCP(4808, factory)
        pp('Starting Web Server...')
        reactor.run()

        
if __name__ == '__main__':
    pythonserver = StreamServer(server_config)
    filter_thread = threading.Thread(target = pythonserver.filter).start()
    render_thread = threading.Thread(target = pythonserver.render).start()
    pythonserver.run()
