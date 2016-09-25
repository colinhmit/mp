# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 17:39:04 2016

@author: colinh
"""

import json, sys,time
from stream.backtest.readers.twitch_reader_template import *
import socket, threading
from sys import argv
import zerorpc
import logging

logging.basicConfig()

test_twitch_config = {
  
  # details required to read Twitch log
  'log_path': '/Users/colinh/Repositories/mp/stream/backtest/logs/',
 
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
  
  # if set to true will display any data received
  'debug': False,

  # if set to true will log all messages from all channels
  # TODO
  'log_messages': False,

  #'mode' : 'python'
  'mode': 'nodejs'
}


class BacktestServer:

    def __init__(self, config, twitch_config, stream):
        #self.config must be set before calling create_socket!
        self.config = config

        self.streams = {}
        self.threads = {}
        self.create_stream(twitch_config, stream)

    #stream control
    def create_stream(self, twitch_config, stream):
        self.threads[stream] = threading.Thread(target=self.add_reader, args=(twitch_config,stream))
        self.threads[stream].start()

    def add_reader(self, twitch_config, stream):
        self.streams[stream] = TwitchReader(twitch_config,stream)
        self.streams[stream].run()

    #js invoked stream call
    def get_stream_trending(self, stream):
        if stream in self.streams.keys():
            if self.config['debug']:
                pp('Found stream!')
            return self.streams[stream].get_trending()

        else:
            if self.config['debug']:
                pp('Invalid stream: stream not found.')

if __name__ == '__main__':
    stream = raw_input('Enter the stream ID: ')
    server = BacktestServer(test_server_config,test_twitch_config,stream)
    s = zerorpc.Server(server)
    s.bind('tcp://0.0.0.0:4242')
    s.run()