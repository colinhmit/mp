import random
import zmq
import pickle
import gc
import re
import multiprocessing

# import utils
from utils._functions_general import *
from input_internal import parse_internal
from input_twitch import parse_twitch
from input_twitter import parse_twitter
from input_reddit import parse_reddit


class InputWorker:
    def __init__(self, config, nlp):
        self.config = config
        self.nlp_parser = nlp

        self.context = zmq.Context()
        self.set_sock()
        self.set_pipe()

        self.process(nlp)

    def set_sock(self):
        self.sock = self.context.socket(zmq.PULL)
        for port in self.config['input_ports']:
            self.sock.connect('tcp://' +
                              self.config['input_host'] +
                              ':' +
                              str(port))

    def set_pipe(self):
        self.pipe_internal = self.context.socket(zmq.PUB)
        self.pipe_internal.connect('tcp://' +
                                   self.config['dist_host'] +
                                   ':' +
                                   str(self.config['dist_port_internal']))
        self.pipe_twitch = self.context.socket(zmq.PUB)
        self.pipe_twitch.connect('tcp://' +
                                 self.config['dist_host'] +
                                 ':' +
                                 str(self.config['dist_port_twitch']))
        self.pipe_twitter = self.context.socket(zmq.PUB)
        self.pipe_twitter.connect('tcp://' +
                                  self.config['dist_host'] +
                                  ':' +
                                  str(self.config['dist_port_twitter']))
        self.pipe_reddit = self.context.socket(zmq.PUB)
        self.pipe_reddit.connect('tcp://' +
                                 self.config['dist_host'] +
                                 ':' +
                                 str(self.config['dist_port_reddit']))

    def process(self):
        nlprefresh = random.randint(500, 1000)
        nlpcounter = 0

        for data in iter(self.sock.recv_string, 'STOP'):
            if data[0:8] == 'internal':
                data = parse_internal(data[8:])
                pipe = self.pipe_internal
            elif data[0:6] == 'twitch':
                data = parse_twitch(data[6:])
                pipe = self.pipe_twitch
            elif data[0:7] == 'twitter':
                data = parse_twitter(data[7:])
                pipe = self.pipe_twitter
            elif data[0:6] == 'reddit':
                data = parse_reddit(data[6:])
                pipe = self.pipe_reddit
            else:
                data = {}

            if len(data) > 0:
                clean_text = re.sub(r"http\S+", "", data['message'])
                clean_text = re.sub(r"[#@]", "", clean_text)
                clean_text = re.sub(r"[^\w\s\'\"!.,&?:;_%-]+", "", clean_text)
                try:
                    data['nlp'] = self.nlp_parser.parse_text(clean_text)
                except Exception, e:
                    data['nlp'] = {}

                if nlpcounter > svorefresh:
                    self.nlp_parser.flush()
                    gc.collect()

                pickled_data = pickle.dumps(data)
                pipe.send(pickled_data)
                nlpcounter += 1
