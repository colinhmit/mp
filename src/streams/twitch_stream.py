# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:42:42 2016

@author: colinh
"""
import datetime
import pickle
import threading

from utils.functions_general import *
from utils.functions_matching import *
from utils.strm import strm

class TwitchStream(strm):
    def __init__(self, config, stream):
        strm.__init__(self, config, stream)

        self.init_threads()

    def init_threads(self):
        #stream helpers
        threading.Thread(target = self.filter_trending_thread).start()
        threading.Thread(target = self.render_trending_thread).start()
        threading.Thread(target = self.garbage_cleanup_thread).start()
        threading.Thread(target = self.reset_subjs_thread).start()

        #data connections
        threading.Thread(target = self.send_stream).start()
        threading.Thread(target = self.send_analytics).start()

    #Main func
    def run(self):
        for data in iter(self.input_socket.recv, 'STOP'):
            msg_data = pickle.loads(data)
            if len(msg_data) == 0:
                pp('Twitch connection was lost...')
            if self.stream == msg_data['channel'][1:].lower():
                messagetime = datetime.datetime.now()
                self.process_message(msg_data, messagetime)  
                self.last_rcv_time = messagetime