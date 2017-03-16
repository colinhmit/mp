# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""
import threading
import multiprocessing

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

from utils.functions_general import *
from reddit_stream import RedditStream
from utils.strm_mgr import strm_mgr

class RedditManager(strm_mgr):
    def __init__(self, config, rddt, init_streams):
        pp('Initializing Reddit Stream Manager...')
        strm_mgr.__init__(self, config, rddt)

        self.curated = []
        self.featured_buffer = []

        for stream in init_streams:
            self.add_stream(stream)

        self.init_featured()
        self.init_threads()

    def init_featured(self):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(self.config['google_sheets']['sheets_key'], self.config['google_sheets']['scopes'])
        self.service = build('sheets', 'v4', credentials=self.credentials)

    def init_threads(self):
        #threading.Thread(target = self.refresh_featured, args=(self.config['twitter_featured'],)).start()
        #threading.Thread(target = self.send_featured, args=(self.config['twitter_featured'],)).start()
        threading.Thread(target = self.garbage_cleanup, args=(self.config['twitter_featured'],)).start()

    def add_stream(self, stream):
        try:
            if stream not in self.streams:
                self.streams[stream] = RedditStream(self.config['reddit_config'], stream) 
                self.src.join_stream(stream)
                self.streams[stream].start()
        except Exception, e:
            pp(e)