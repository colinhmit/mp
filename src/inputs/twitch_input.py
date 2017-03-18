# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:55:12 2016

@author: colinh
"""
import multiprocessing
import re

#import utils
from utils.functions_general import *
from std_inpt import std_inpt

class TwitchInput(std_inpt):
    def __init__(self, config, init_streams, nlp):
        std_inpt.__init__(self, config, nlp)
        pp('Initializing Twitch Input Server...')
        
        #distribute
        multiprocessing.Process(target=self.distribute).start()

        for _ in xrange(self.config['num_procs']):
            multiprocessing.Process(target=self.process, args=(self.nlp_parser,)).start()
    
    def parse(self, data):
        msg = {
                'channel': re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0],
                'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
                'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0],
                'media_url': [],
                'mp4_url': '',
                'id': ''
                }
        return msg