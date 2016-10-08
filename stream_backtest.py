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
import boto3

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
  #'mode': 'nodejs'
  'mode': 'sqs'
}


class BacktestServer:

    def __init__(self, config, twitch_config, log, stream):
        #self.config must be set before calling create_socket!
        self.config = config
        self.init_socket()

        self.streams = {}
        self.threads = {}
        self.urls = {}
        self.create_stream(twitch_config, log, stream)

    def init_socket(self):
        if self.config['mode'] == 'python':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            sock.bind((self.config['host'], self.config['port']))
            sock.listen(self.config['listeners'])
            self.socket = sock

        if self.config['mode'] == 'sqs':
            session = boto3.Session(
                aws_access_key_id='AKIAJJYQ67ESV5S4YVHQ',
                aws_secret_access_key='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',
                region_name='us-west-2',
            )
            self.client = session.client('sqs')

    #stream control
    def create_stream(self, twitch_config, log, stream):
        self.threads[stream] = threading.Thread(target=self.add_reader, args=(twitch_config,log, stream))
        self.threads[stream].start()

    def add_reader(self, twitch_config, log, stream):
        self.streams[stream] = TwitchReader(twitch_config,log)

        if self.config['mode'] == 'sqs':
            queue_name = 'mpq-' + stream
            response = self.client.create_queue(QueueName=queue_name)
            self.urls[stream] = response['QueueUrl']

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

    #sqs msging
    def multicast_trending(self):
        while True:
            if len(self.urls.keys()) > 0:
                for stream_key in self.urls.keys():
                    stream_url = self.urls[stream_key]
                    stream_dict = json.dumps(self.streams[stream_key].get_trending())
                    if self.config['debug']:
                        pp(stream_dict)
                    response = self.client.send_message(
                        QueueUrl=stream_url,
                        MessageBody=stream_dict,
                        DelaySeconds=0,
                    )
            else:
                pass

            time.sleep(0.5)


if __name__ == '__main__':
    log = raw_input('Enter the stream log ID: ')
    stream = raw_input('Enter the stream test ID: ')
    server = BacktestServer(test_server_config,test_twitch_config,log,stream)
    multicast_thread = threading.Thread(target = server.multicast_trending).start()
