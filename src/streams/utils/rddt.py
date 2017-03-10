# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:55:12 2016

@author: colinh
"""
import threading
import multiprocessing
import zmq
import Queue
import gc
import json

import praw

from functions_general import *

class rddt:
    def __init__(self, config, init_streams):
        self.config = config
        self.init_streams = init_streams
        self.streams = init_streams
        self.set_rddt_obj()

        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams)>0:
            self.stream_conn.start()

    def set_rddt_obj(self):
        self.reddit = praw.Reddit(client_id=self.config['client_token'],
                     client_secret=self.config['client_secret'],
                     user_agent=self.config['user_agent'])

    def stream_connection(self):
        #set up subreddits
        self.Q = Queue.Queue()
        for stream in self.streams:
            threading.Thread(target=self.subreddit_monitor, args=(stream,)).start()

        #set up zmq
        context = zmq.Context()
        self.pipe = context.socket(zmq.PUSH)
        connected = False
        while not connected:
            try:
                self.pipe.bind("tcp://127.0.0.1:"+str(self.config['zmq_rddt_port']))
                connected = True
            except Exception, e:
                pass

        self.alive = True
        while self.alive:
            data = self.Q.get()
            self.pipe.send_string("%s%s" % ("|src:reddit|", data))

    def subreddit_monitor(self, stream):
        subreddit = self.reddit.subreddit(stream)
        subcontent = {}

        scraping = True
        while scraping:
            if len(subcontent)>1000:
                subcontent = {}

            maxdiff = 0
            maxsubmission = None
            subreddithot = subreddit.hot(limit=100)
            for submission in subreddithot:
                if submission.id not in subcontent:
                    subcontent[submission.id] = submission.score
                else:
                    if (submission.score - subcontent[submission.id])>maxdiff:
                        maxdiff = submission.score - subcontent[submission.id]
                        maxsubmission = submission
                    subcontent[submission.id] = submission.score
            if maxsubmission:
                if not maxsubmission.author:
                    data = {
                            'subreddit': stream,
                            'username': 'deleted',
                            'message': maxsubmission.title,
                            'media_url': maxsubmission.url,
                            'id': maxsubmission.id
                            }
                else:
                    data = {
                            'subreddit': stream,
                            'username': maxsubmission.author.name,
                            'message': maxsubmission.title,
                            'media_url': maxsubmission.url,
                            'id': maxsubmission.id
                            }
                self.Q.put(json.dumps(data))                    
            
    def refresh_streams(self):
        pp('Refreshing streams...')
        if self.stream_conn.is_alive():
            self.stream_conn.terminate()
        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams)>0:
            self.stream_conn.start()

    def reset_streams(self):
        pp('Resetting streams...')
        self.streams = self.init_streams
        if self.stream_conn.is_alive():
            self.stream_conn.terminate()
        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams)>0:
            self.stream_conn.start()

    def join_stream(self, stream):
        if stream not in self.streams:
            pp('Joining stream %s' % stream)
            if self.stream_conn.is_alive():
                self.stream_conn.terminate()
            self.streams.append(stream)
            self.stream_conn = multiprocessing.Process(target=self.stream_connection)
            self.stream_conn.start()

    def leave_stream(self, stream):
        if stream in self.streams:
            self.streams.remove(stream)
            if self.stream_conn.is_alive():
                self.stream_conn.terminate()
            self.stream_conn = multiprocessing.Process(target=self.stream_connection)
            if len(self.streams)>0:
                self.stream_conn.start()
            else:
                pp('No streams to stream from...')

    def batch_streams(self, streams_to_add, streams_to_remove):
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
