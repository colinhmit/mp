import random
import zmq
import pickle
import json
import gc
import re
import importlib
import multiprocessing

# import utils
from utils._functions_general import *


class InputWorker:
    def __init__(self, config, inputs, nlp):
        self.config = config
        self.inputs = inputs
        self.nlp_parser = nlp

        self.context = zmq.Context()
        self.set_sock()
        self.set_pipes()
        self.set_parsers()

        self.process()

    def set_sock(self):
        self.sock = self.context.socket(zmq.PULL)
        for input_ in self.inputs:
            self.sock.connect('tcp://' +
                              self.config['input_host'] +
                              ':' +
                              str(self.config['input_ports'][input_]))

    def set_pipes(self):
        self.pipe = {}
        for input_ in self.inputs:
            self.pipe[input_] = self.context.socket(zmq.PUB)
            self.pipe[input_].connect('tcp://' +
                                      self.config['dist_host'] +
                                      ':' +
                                      str(self.config['dist_ports'][input_]))

    def set_parsers(self):
        self.parsers = {}
        for input_ in self.inputs:
            module = importlib.import_module(self.config['modules'][input_])
            self.parsers[input_] = getattr(module, 'parse')

    def process(self):
        nlprefresh = random.randint(500, 1000)
        nlpcounter = 0

        for data in iter(self.sock.recv_string, 'STOP'):
            data = json.loads(data)
            # data could be corrupt or src could not be present?
            try:
                pipe = self.pipe[data['src']]
                data = self.parsers[data['src']](data['data'])
            except Exception, e:
                pp('process data failed', 'error')
                pp(e, 'error')
                data = {}
        
            if len(data) > 0:
                clean_text = re.sub(r"http\S+", "", data['message'])
                clean_text = re.sub(r"[#@]", "", clean_text)
                clean_text = re.sub(r"[^\w\s\'\"!.,&?:;_%-]+", "", clean_text)
                try:
                    data['nlp'] = self.nlp_parser.parse_text(clean_text)
                except Exception, e:
                    data['nlp'] = {}

                if nlpcounter > nlprefresh:
                    self.nlp_parser.flush()
                    gc.collect()

                pickled_data = pickle.dumps(data)
                pipe.send(pickled_data)
                nlpcounter += 1
