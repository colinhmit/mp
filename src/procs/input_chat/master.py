import multiprocessing

# import utils
from src.utils._functions_general import *
from src.procs.input_chat.nlp import NLPParser
from src.procs.input_chat.worker import Worker
from src.procs.input_chat.distributor import Distributor


class InputChatMaster:
    def __init__(self, config):
        pp('Initializing Input Chat Master...')
        self.config = config
        self.nlp_parser = NLPParser()

        self.dists = []
        self.workers = []

        self.start_dists()
        self.start_workers()

    def start_dists(self):
        for src in self.config['dist_config'].keys():
            self.dists.append(multiprocessing.Process(target=Distributor,
                                                      args=(self.config['dist_config'][src],)
                                                     ).start())

    def restart_dists(self):
        for dist in self.dists:
            if dist.is_alive():
                dist.terminate()
        self.dists = []
        for src in self.config['dist_config'].keys():
            self.dists.append(multiprocessing.Process(target=Distributor,
                                                      args=(self.config['dist_config'][src],)
                                                     ).start())

    def start_workers(self):
        for _ in xrange(self.config['num_workers']):
            self.workers.append(multiprocessing.Process(target=Worker,
                                                        args=(self.config['worker_config'],
                                                              self.nlp_parser,)
                                                       ).start())

    def restart_workers(self):
        for worker in self.workers:
            if worker.is_alive():
                worker.terminate()
        self.workers = []    
        for _ in xrange(self.config['num_workers']):
            self.workers.append(multiprocessing.Process(target=Worker,
                                                        args=(self.config['worker_config'],
                                                              self.nlp_parser,)
                                                       ).start())
