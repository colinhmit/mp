# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 17:39:04 2016

@author: colinh
"""

import json
import sys
import time
import socket
import logging
import threading
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from readers.twitch_reader_template import *
logging.basicConfig()

test_twitch_config = {
  # details required to read Twitch log
  'log_path': '/Users/colinh/Repositories/mp/replay/logs/',
 
  # if set to true will display any data received
  'debug': False,

  # if set to true will log all messages from all channels
  # TODO
  'log_messages': False,

  #fw_eo output from funcions_matching threshold 
  'fo_compare_threshold': 65,
  'so_compare_threshold': 80,
  
  #twitch_stream trending params
  'matched_init_base': 20,
  'matched_add_base': 20,
  
  'decay_msg_base': 1,
  'decay_time_base': 1,
  
  #output frequency
  'output_freq': 1                  
}

test_server_config = {
  'host': '127.0.0.1',
  'port': 4808,
  # if set to true will display any data received
  'debug': False,

  # if set to true will log all messages from all channels
  # TODO
  'log_messages': False,

  #'mode' : 'python'
  #'mode': 'nodejs'
  'mode': 'sqs'
}

class WebServer(BaseHTTPRequestHandler):
    stream_server = None

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        output = self.handle_GET(self.path)
        #pp(output)
        self.wfile.write(output)

    #get control
    def handle_GET(self, path):
        #stream request
        if path[0:8] == '/stream/':
            return self.stream_server.get_stream(path[8:])
        else:
            return json.dumps('Invalid path! Valid paths: /stream/')

class ReplayServer():

    def __init__(self, config, twitch_config, log, stream, ts):
        pp('Initializing Stream Server...')
        #self.config must be set before calling create_socket!
        self.config = config
        self.streams = {}
        self.threads = {}
        self.create_stream(twitch_config, log, stream, ts)

    #stream control
    def create_stream(self, twitch_config, log, stream, ts):
        self.threads[stream] = threading.Thread(target=self.add_reader, args=(twitch_config, log, stream, ts))
        self.threads[stream].start()

    def add_reader(self, twitch_config, log, stream, ts):
        self.streams[stream] = TwitchReader(twitch_config,log)
        self.streams[stream].run(ts)

    def get_stream(self, stream_id):
        config = self.config
        if stream in self.streams.keys():
            if self.config['debug']:
                pp('Found stream!')
            output = json.dumps(self.streams[stream_id].get_trending())
        else:
            if self.config['debug']:
                pp('Invalid stream: stream not found.')
            output = json.dumps({})
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

    def restart_threads(self, config, ts):
        for stream_key in self.streams.keys():
            self.streams[stream_key].stop = True

        self.streams = {}
        self.threads = {}
        self.create_stream(config, log, stream, ts)


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
    log = raw_input('Enter the stream log ID: ')
    stream = raw_input('Enter the stream test ID: ')
    ts = float(raw_input('Enter the start time (s): '))
    pythonserver = ReplayServer(test_server_config,test_twitch_config,log,stream, ts)
    filter_thread = threading.Thread(target = pythonserver.filter).start()
    render_thread = threading.Thread(target = pythonserver.render).start()
    server_thread = threading.Thread(target = pythonserver.run).start()

    while True:
        ts = raw_input('Enter a time to restart @:')
        print '\nPausing...'
        pythonserver.restart_threads(test_twitch_config, float(ts))
