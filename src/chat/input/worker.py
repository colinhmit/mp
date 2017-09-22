import random
import zmq
import pickle
import json
import gc
import re
import importlib
import multiprocessing

# import utils
from src.utils._functions_general import *


class InputWorker:
    def __init__(self, config, nlp):
        self.config = config
        self.nlp_parser = nlp

        self.context = zmq.Context()
        self.set_sock()
        self.set_pipes()
        self.set_parsers()

        self.process()

    def set_sock(self):
        self.sock = self.context.socket(zmq.PULL)
        for src in self.config['input_ports'].keys():
            self.sock.connect('tcp://' +
                              self.config['input_host'] +
                              ':' +
                              str(self.config['input_ports'][src]))

    def set_pipes(self):
        self.pipe = {}
        for src in self.config['dist_ports'].keys():
            self.pipe[src] = self.context.socket(zmq.PUB)
            self.pipe[src].connect('tcp://' +
                                      self.config['dist_host'] +
                                      ':' +
                                      str(self.config['dist_ports'][src]))

    def set_parsers(self):
        self.parsers = {}
        for src in self.config['modules'].keys():
            module = importlib.import_module(self.config['modules'][src])
            self.parsers[src] = getattr(module, 'parse')

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
