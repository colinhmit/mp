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

#This is a basic listener that just prints received tweets to stdout.
class StdTwtrListener(StreamListener):
    def __init__(self, input_port):
        self.port = input_port
        self.pipe = None

    def on_data(self, data):
        self.pipe.send_string("%s %s" % ("|src:twitter|", data))
        return True

    def on_error(self, status):
        pp(status)

    def on_timeout(self):
        pp('Timeout...')

class twtr:
    def __init__(self, config, init_streams):
        self.config = config
        self.init_streams = init_streams
        self.streams = init_streams
        self.set_twtr_stream_object()

        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams)>0:
            self.stream_conn.start()

    def set_twtr_stream_object(self):
        self.l = StdTwtrListener(self.config['zmq_twtr_port'])
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
                self.l.pipe.bind("tcp://127.0.0.1:"+str(self.l.port))
                connected = True
            except Exception, e:
                pass

        try:
            pp('Connecting to target streams...')
            self.stream_obj.filter(track=self.streams)
            gc.collect()
        except Exception, e:
            pp('/////////////////STREAM CONNECTION WENT DOWN////////////////////')
            pp(e)

    def refresh_streams(self):
        pp('Refreshing streams...')
        if self.stream_conn.is_alive():
            self.stream_obj.disconnect()
            self.stream_conn.terminate()
        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams)>0:
            self.stream_conn.start()

    def reset_streams(self):
        pp('Resetting streams...')
        self.streams = self.init_streams
        if self.stream_conn.is_alive():
            self.stream_obj.disconnect()
            self.stream_conn.terminate()
        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams)>0:
            self.stream_conn.start()

    def join_stream(self, stream):
        if stream not in self.streams:
            pp('Joining stream %s' % stream)
            if self.stream_conn.is_alive():
                self.stream_obj.disconnect()
                self.stream_conn.terminate()
            self.streams.append(stream)
            self.stream_conn = multiprocessing.Process(target=self.stream_connection)
            self.stream_conn.start()

    def leave_stream(self, stream):
        if stream in self.streams:
            self.streams.remove(stream)
            if self.stream_conn.is_alive():
                self.stream_obj.disconnect()
                self.stream_conn.terminate()
            self.stream_conn = multiprocessing.Process(target=self.stream_connection)
            if len(self.streams)>0:
                self.stream_conn.start()
            else:
                pp('No streams to stream from...')

    def batch_streams(self, streams_to_add, streams_to_remove):
        pp('Batching streams. Adding: '+str(streams_to_add)+', Deleting: '+str(streams_to_remove))
        if self.stream_conn.is_alive():
            self.stream_obj.disconnect()
            self.stream_conn.terminate()
        for stream in streams_to_remove:
            if stream in self.streams:
                self.streams.remove(stream)
        for stream in streams_to_add:
            if stream not in self.streams:
                self.streams.append(stream)
        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams)>0:
            self.stream_conn.start()