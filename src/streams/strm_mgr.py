# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""
import re
import time
import zmq
import requests
import pickle

from utils.functions_general import *

class strm_mgr:
    def __init__(self, config, src):
        self.config = config
        self.src = src

        self.streams = {}
        self.featured = []

        self.pattern = re.compile('[^\w\s\'\"!.,$&?:;_-]+')
        self.init_sockets()

    def init_sockets(self):
        context = zmq.Context()
        self.http_socket = context.socket(zmq.PUSH)
        self.http_socket.connect('tcp://'+self.config['zmq_http_host']+':'+str(self.config['zmq_http_port']))

    def delete_stream(self, stream):
        if stream in self.streams:
            try:
                self.streams[stream].terminate()
                del self.streams[stream]
                self.src.leave_stream(stream)
            except Exception, e:
                pp(e)

    # Helper threads
    def refresh_featured(self, config):
        self.refresh_loop = True
        while self.refresh_loop:
            self.get_featured()
            time.sleep(config['refresh_featured_timeout'])

    def get_featured(self):
        pass

    def send_featured(self, config):
        self.send_featured_loop = True
        while self.send_featured_loop:
            try:
                data = {
                    'type': 'featured',
                    'src': config['self'],
                    'data': self.featured
                }
                pickled_data = pickle.dumps(data)
                self.http_socket.send(pickled_data)
            except Exception, e:
                pp(e)
            time.sleep(config['refresh_featured_timeout'])