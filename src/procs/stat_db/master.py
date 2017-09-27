import multiprocessing

# import utils
from src.utils._functions_general import *
from src.procs.stat_db.input_chat_stats import InputChatStats


class StatDBMaster:
    def __init__(self, config):
        pp('Initializing Stat DB Master...')
        self.config = config

        self.input_chat_stats = multiprocessing.Process(target=InputChatStats,
                                  args=(self.config['input_chat_stats_config'],))
        self.input_chat_stats.start()
