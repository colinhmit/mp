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
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json

logging.basicConfig()

class WebServer(BaseHTTPRequestHandler):
    stream_server = None

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        output = self.handle_GET(self.path)
        
        self.wfile.write(output)

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
        newStream = TwitchStream(twitch_config,stream)
        newStream.run()
        self.streams[stream] = newStream

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

    def filter_clean(self):
        self.filter_clean_loop = True

        while self.filter_clean_loop:
            if len(self.streams.keys()) > 0:
                for stream_key in self.streams.keys():
                    self.streams[stream_key].preprocess_trending()
                    self.streams[stream_key].filter_trending()
                    
            else:
                pass

            time.sleep(0.4)

    def run(self):
        pp('Initializing Web Server...')
        WebServer.stream_server = self
        #prod aws
        server = HTTPServer((self.config['host'], self.config['port']), WebServer)
        #local testing
        #server = HTTPServer(('127.0.0.1', 4808), WebServer)

        pp('Starting Web Server...')
        server.serve_forever()

if __name__ == '__main__':
    pythonserver = StreamServer(server_config)
    filter_thread = threading.Thread(target = pythonserver.filter_clean).start()

    pythonserver.run()
