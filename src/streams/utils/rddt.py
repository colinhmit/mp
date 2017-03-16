# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:55:12 2016

@author: colinh
"""
import threading
import multiprocessing
import zmq
import Queue
import json

import praw

from functions_general import *
from inpt import inpt

class rddt(inpt):
    def __init__(self, config, init_streams):
        inpt.__init__(self, config, init_streams)
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
                self.pipe.bind('tcp://'+self.config['zmq_host']+':'+str(self.config['zmq_port']))
                connected = True
            except Exception, e:
                pass

        self.alive = True
        while self.alive:
            data = self.Q.get()
            self.pipe.send_string(data)

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
