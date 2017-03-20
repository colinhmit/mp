# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:55:12 2016
@author: colinh
"""
#Import the necessary methods from tweepy library
import multiprocessing
import zmq
import gc

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

from functions_general import *
from inpt import inpt

#This is a basic listener that just prints received tweets to stdout.
class StdTwtrListener(StreamListener):
    def __init__(self, input_port):
        self.port = input_port
        self.pipe = None

    def on_data(self, data):
        self.pipe.send_string(data)
        return True

    def on_error(self, status):
        pp(status)

    def on_timeout(self):
        pp('Timeout...')

class twtr(inpt):
    def __init__(self, config, init_streams):
        inpt.__init__(self, config, init_streams)
        self.set_twtr_stream_object()

        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams)>0:
            self.stream_conn.start()

    def set_twtr_stream_object(self):
        self.l = StdTwtrListener(self.config['zmq_input_port'])
        self.auth = OAuthHandler(self.config['consumer_token'], self.config['consumer_secret'])
        self.auth.set_access_token(self.config['access_token'], self.config['access_secret'])
        self.api = API(self.auth)
        self.stream_obj = Stream(self.auth, self.l)

    def stream_connection(self):
        context = zmq.Context()
        self.l.pipe = context.socket(zmq.PUSH)
        connected = False
        while not connected:
            try:
                self.l.pipe.bind('tcp://'+self.config['zmq_input_host']+':'+str(self.l.port))
                connected = True
            except Exception, e:
                pass

        try:
            pp('Connecting to twitter...')
            self.stream_obj.filter(track=self.streams)
            gc.collect()
        except Exception, e:
            pp('/////////////////STREAM CONNECTION WENT DOWN////////////////////')
            pp(e)