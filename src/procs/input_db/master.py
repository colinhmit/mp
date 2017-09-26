import multiprocessing

# import utils
from src.utils._functions_general import *
from src.procs.input_db.worker import Worker
from src.procs.input_db.funnel import Funnel


class InputDBMaster:
    def __init__(self, config):
        pp('Initializing Input Chat Master...')
        self.config = config

        self.funnels = []
        self.input_chat_funnel = multiprocessing.Process(target=Funnel,
                                  args=(self.config['input_chat_funnel_config'],))
        self.input_chat_funnel.start()
        self.stream_chat_funnel = multiprocessing.Process(target=Funnel,
                                  args=(self.config['stream_chat_funnel_config'],))
        self.stream_chat_funnel.start()
        self.workers = []

        self.start_workers()

    def start_workers(self):
        for _ in xrange(self.config['num_workers']):
            self.workers.append(multiprocessing.Process(target=Worker,
                                                        args=(self.config['worker_config'],)
                                                       ).start())

    def restart_workers(self):
        for worker in self.workers:
            if worker.is_alive():
                worker.terminate()
        self.workers = []    
        for _ in xrange(self.config['num_workers']):
            self.workers.append(multiprocessing.Process(target=Worker,
                                                        args=(self.config['worker_config'],)
                                                       ).start())
