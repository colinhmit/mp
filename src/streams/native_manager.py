# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""
import threading
import multiprocessing
import requests
import json

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

from utils.functions_general import *
from utils.native_stream import NativeStream
from strm_mgr import strm_mgr

class NativeManager(strm_mgr):
    def __init__(self, config):
        pp('Initializing Native Stream Manager...')
        strm_mgr.__init__(self, config, config['native_config']['self'], None)

        self.init_featured()
        self.init_threads()

    def init_featured(self):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(self.config['google_sheets']['sheets_key'], self.config['google_sheets']['scopes'])
        self.service = build('sheets', 'v4', credentials=self.credentials)

    def init_threads(self):
        # threading.Thread(target = self.refresh_featured, args=(self.config['twitch_featured'],)).start()
        # threading.Thread(target = self.send_featured, args=(self.config['twitch_featured'],)).start()
        pass

    def add_stream(self, stream):
        try:
            if stream not in self.streams:
                self.streams[stream] = multiprocessing.Process(target=NativeStream, args=(self.config['native_config'], stream)) 
                self.streams[stream].start()
        except Exception, e:
            pp(e)

    def delete_stream(self, stream):
        if stream in self.streams:
            try:
                self.streams[stream].terminate()
                del self.streams[stream]
                self.send_delete([stream])
            except Exception, e:
                pp(e)