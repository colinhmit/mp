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

from readers.twitch_reader_template import *
logging.basicConfig()

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site

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
      'matched_init_base': 50,
      'matched_add_base': 15,
      'matched_add_user_base':500,

      'buffer_mult': 4,
      
      'decay_msg_base': 1,
      'decay_msg_min_limit': 0.4,
      'decay_time_mtch_base': 4,
      'decay_time_base': 0.2,
                       
  # maximum amount of bytes to receive from socket - 1024-4096 recommended
  'socket_buffer_size': 4096            
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

class WebServer(Resource):

    isLeaf = True
    stream_server = None
    
    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        output = self.handle_GET(request.path, request.args)
        return output

    #get control
    def handle_GET(self, path, args):
        #stream request
        if path[0:7] == '/stream':
            return self.stream_server.get_agg_streams(args)
        else:
            return json.dumps('Invalid path! Valid paths: /stream/')

class ReplayServer():

    def __init__(self, config, reader_config):
        pp('Initializing Stream Server...')
        #self.config must be set before calling create_socket!
        self.config = config
        self.streams = {}
        self.reader_config = reader_config

    #stream control
    def create_stream(self, log, ts):
        threading.Thread(target=self.add_reader, args=(log, ts)).start()

    def add_reader(self, log, ts):
        self.streams[log] = TwitchReader(self.reader_config,log)
        self.streams[log].run(ts)

    def get_agg_streams(self, args):
        config = self.config
        trend_dicts = []

        if ('twitch' in args.keys()) and (len(args['twitch'][0])>0):
            for stream_id in args['twitch'][0].split(','):
                trend_dicts.append(self.get_stream(stream_id))
        if ('twitter' in args.keys()) and (len(args['twitter'][0])>0):
            for stream_id in args['twitter'][0].split(','):
                trend_dicts.append(self.get_stream(stream_id))
        
        output = {}
        [output.update(d) for d in trend_dicts]
        return json.dumps(output)

    
    def get_stream(self, stream_id):
        config = self.config
        stream_id = stream_id.lower()

        if not stream_id in self.streams.keys():
            self.create_stream(stream_id, 0)
            stream_exists = False
            while not stream_exists:
                stream_exists = stream_id in self.streams.keys()

        output = self.streams[stream_id].get_trending()
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
            time.sleep(0.17)

    def restart_threads(self, config, ts):
        for stream_key in self.streams.keys():
            self.streams[stream_key].stop = True

        self.streams = {}
        self.threads = {}
        self.create_stream(config, log, stream, ts)


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
    pythonserver = ReplayServer(test_server_config,test_twitch_config)
    filter_thread = threading.Thread(target = pythonserver.filter).start()
    render_thread = threading.Thread(target = pythonserver.render).start()
    #server_thread = threading.Thread(target = pythonserver.run).start()
    pythonserver.run()
    # while True:
    #     ts = raw_input('Enter a time to restart @:')
    #     print '\nPausing...'
    #     pythonserver.restart_threads(test_twitch_config, float(ts))
