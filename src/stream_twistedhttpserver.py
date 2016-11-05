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

logging.basicConfig()

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site

from streams.twitch_stream import *
from streams.twitter_stream import *
from config.universal_config import *

import streams.lib.twtr as twtr_

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
            if path[7:15] == '/twitch/':
                return self.stream_server.get_stream(path[15:], 'twitch')
            elif path[7:16] == '/twitter/':
                return self.stream_server.get_stream(path[16:], 'twitter')
            else:
                return json.dumps('Invalid path! Valid paths: /stream/twitch/ & /stream/twitter/')
        else:
            return json.dumps('Invalid path! Valid paths: /stream/')

class StreamServer():
    def __init__(self, config):
        pp('Initializing Stream Server...')
        self.config = config

        self.twitch_streams = {}
        self.twitter_streams = {}
        self.threads = {}

        #twitter
        self.twit = twtr_.twtr(twitter_config)

    #stream control
    def create_stream(self, stream, src):
        self.threads[stream] = threading.Thread(target=self.add_stream, args=(stream,src))
        self.threads[stream].start()

    def add_stream(self, stream, src):
        if src == 'twitch':
            self.twitch_streams[stream] = TwitchStream(twitch_config, stream)
            self.twitch_streams[stream].run()
        elif src == 'twitter':
            self.twitter_streams[stream] = TwitterStream(twitch_config, stream, self.twit)
            self.twitter_streams[stream].run()
        else:
            pass

    def get_stream(self, stream_id, src):
        config = self.config
        stream_id = stream_id.lower()

        if src == 'twitch':
            if stream_id in self.twitch_streams.keys():
                if config['debug']:
                    pp('Found stream!')
            else:
                if config['debug']:
                    pp('Stream not found.')
                self.create_stream(stream_id, src)
                stream_exists = False
                while not stream_exists:
                    stream_exists = stream_id in self.twitch_streams.keys()
                if config['debug']:
                    pp('Stream created!')
            output = json.dumps(self.twitch_streams[stream_id].get_trending())

        elif src == 'twitter':
            if stream_id in self.twitter_streams.keys():
                if config['debug']:
                    pp('Found stream!')
            else:
                if config['debug']:
                    pp('Stream not found.')
                self.create_stream(stream_id, src)
                stream_exists = False
                while not stream_exists:
                    stream_exists = stream_id in self.twitter_streams.keys()
                if config['debug']:
                    pp('Stream created!')
            output = json.dumps(self.twitter_streams[stream_id].get_trending())
        
        else:
            output = json.dumps({'NOT FOUND'})

        if config['debug']:
            pp('Sending: '+ output)
        return output

    def filter_twitch(self):
        self.filter_loop = True
        while self.filter_loop:
            if len(self.twitch_streams.keys()) > 0:
                for stream_key in self.twitch_streams.keys():
                    self.twitch_streams[stream_key].filter_trending()
            else:
                pass
            time.sleep(0.8)

    def render_twitch(self):
        self.clean_loop = True
        while self.clean_loop:
            if len(self.twitch_streams.keys()) > 0:
                for stream_key in self.twitch_streams.keys():
                    self.twitch_streams[stream_key].render_trending()
            else:
                pass
            time.sleep(0.2)

    def filter_twitter(self):
        self.filter_loop = True
        while self.filter_loop:
            if len(self.twitter_streams.keys()) > 0:
                for stream_key in self.twitter_streams.keys():
                    self.twitter_streams[stream_key].filter_trending()
            else:
                pass
            time.sleep(0.8)

    def render_twitter(self):
        self.clean_loop = True
        while self.clean_loop:
            if len(self.twitter_streams.keys()) > 0:
                for stream_key in self.twitter_streams.keys():
                    self.twitter_streams[stream_key].render_trending()
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
    filter_twitch_thread = threading.Thread(target = pythonserver.filter_twitch).start()
    render_twitch_thread = threading.Thread(target = pythonserver.render_twitch).start()
    filter_twitter_thread = threading.Thread(target = pythonserver.filter_twitter).start()
    render_twitter_thread = threading.Thread(target = pythonserver.render_twitter).start()
    pythonserver.run()
