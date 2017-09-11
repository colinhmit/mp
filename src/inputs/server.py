import multiprocessing
import importlib

# import utils
from utils._functions_general import *
from utils.nlp import NLPParser
from worker import InputWorker
from distributor import InputDistributor


class InputServer:
    def __init__(self, config):
        pp('Initializing Input Server...')
        self.config = config
        self.nlp_parser = NLPParser()

        self.inputs = {}
        for input_ in self.config['inputs']:
            if self.config['on'][input_]:
                class_ = getattr(importlib.import_module(self.config['modules'][input_]), 'Input')
                self.inputs[input_] = class_(self.config['input_configs'][input_])
                multiprocessing.Process(target=InputDistributor,
                                    args=(self.config['input_configs'][input_],)
                                    ).start()

        for _ in xrange(self.config['num_workers']):
            multiprocessing.Process(target=InputWorker,
                                    args=(self.config['worker_config'],
                                          self.inputs.keys(),
                                          self.nlp_parser,)
                                    ).start()
