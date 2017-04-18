import re
import json
import multiprocessing
import datetime
import random
import zmq
import pickle
import gc

#import utils
from inputs.utils.mnl import mnl, mnlWebServer
from inputs.utils.twtr import twtr
from inputs.utils.rddt import rddt
from inputs.utils.irc import irc
from inputs.native_input import NativeInput
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

        #self.mnl = mnl(self.config['mnl_config'])
        self.irc = irc(self.config['irc_config'], init_streams['twitch'])
        self.twtr = twtr(self.config['twtr_config'], init_streams['twitter'])
        #self.rddt = rddt(self.config['rddt_config'], init_streams['reddit'])

        #self.native_input = NativeInput(self.config['mnl_config'], self.nlp_parser)
        self.twitch_input = TwitchInput(self.config['irc_config'], self.nlp_parser)
        self.twitter_input = TwitterInput(self.config['twtr_config'], self.nlp_parser)
        #self.reddit_input = RedditInput(self.config['rddt_config'], self.nlp_parser)