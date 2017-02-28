# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:42:42 2016

@author: colinh
"""
import datetime
import pickle

from utils.functions_general import *
from utils.functions_matching import *
from utils.strm import strm

class TwitchStream(strm):
    def __init__(self, config, stream):
        strm.__init__(self, config, stream)

    #Main func
    def run(self):
        while not self.kill:
            raw_data = self.data_socket.recv()
            msg_data = pickle.loads(raw_data[self.config['zmq_cutoff']:])
            if len(msg_data) == 0:
                pp('Twitch connection was lost...')
            if self.stream == msg_data['channel'][1:].lower():
                messagetime = datetime.datetime.now()
                self.process_message(msg_data, messagetime)  
                self.last_rcv_time = messagetime