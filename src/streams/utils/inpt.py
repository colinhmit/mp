# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:55:12 2016

@author: colinh
"""
import multiprocessing

from functions_general import *

#Input Framework
class inpt:
    def __init__(self, config, init_streams):
        self.config = config
        self.init_streams = init_streams
        self.streams = init_streams
        self.stream_conn = None

    def refresh_streams(self):
        pp(self.config['self']+' Refreshing streams...')
        if self.stream_conn.is_alive():
            self.stream_conn.terminate()
        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams)>0:
            self.stream_conn.start()

    def reset_streams(self):
        pp(self.config['self']+' Resetting streams...')
        self.streams = self.init_streams
        if self.stream_conn.is_alive():
            self.stream_conn.terminate()
        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams)>0:
            self.stream_conn.start()

    def join_stream(self, stream):
        if stream not in self.streams:
            pp(self.config['self']+' Joining stream %s.' % stream)
            if self.stream_conn.is_alive():
                self.stream_conn.terminate()
            self.streams.append(stream)
            self.stream_conn = multiprocessing.Process(target=self.stream_connection)
            self.stream_conn.start()

    def leave_stream(self, stream):
        if stream in self.streams:
            pp(self.config['self']+' Leaving stream %s.' % stream)
            self.streams.remove(stream)
            if self.stream_conn.is_alive():
                self.stream_conn.terminate()
            self.stream_conn = multiprocessing.Process(target=self.stream_connection)
            if len(self.streams)>0:
                self.stream_conn.start()
            else:
                pp(self.config['self']+' No streams to stream from...')

    def batch_streams(self, streams_to_add, streams_to_remove):
        pp(self.config['self']+' Batching streams...')
        if self.stream_conn.is_alive():
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