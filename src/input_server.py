# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:55:12 2016

@author: colinh
"""
#Import the necessary methods from tweepy library
import re
import json
import multiprocessing
import datetime
import random
import zmq
import pickle
import gc

#import utils
from inputs.twitch_input import TwitchInput
from inputs.twitter_input import TwitterInput
from inputs.reddit_input import RedditInput
from inputs.utils.nlp import nlpParser
from inputs.utils.functions_general import *

class InputServer:
    def __init__(self, config, init_streams):
        pp('Initializing Input Server...')
        self.config = config
        self.nlp_parser = nlpParser()

        self.twitch_input = TwitchInput(self.config['irc_config'], init_streams['twitch'], self.nlp_parser)
        self.twitter_input = TwitterInput(self.config['twtr_config'], init_streams['twitter'], self.nlp_parser)
        self.reddit_input = RedditInput(self.config['rddt_config'], init_streams['reddit'], self.nlp_parser)