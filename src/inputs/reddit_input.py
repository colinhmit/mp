# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:55:12 2016

@author: colinh
"""
import json
import multiprocessing

#import utils
from inputs.utils.functions_general import *
from std_inpt import std_inpt

class RedditInput(std_inpt):
    def __init__(self, config, nlp):
        std_inpt.__init__(self, config, nlp)
        pp('Initializing Reddit Input Server...')

        #distribute
        multiprocessing.Process(target=self.distribute).start()

        for _ in xrange(self.config['num_procs']):
            multiprocessing.Process(target=self.process, args=(self.nlp_parser,)).start()
    
    def parse(self, data):
        jsondata = json.loads(data)
        msg = {
                'src': 'reddit',
                'subreddit': jsondata['subreddit'],
                'username': jsondata['username'],
                'message': jsondata['message'],
                'media_url': [jsondata['media_url']],
                'mp4_url': '',
                'id': jsondata['id']
                }
        return msg