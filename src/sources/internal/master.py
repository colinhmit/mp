import multiprocessing

from src.utils._functions_general import *
from src.sources.internal.chat import Chat
from src.sources.internal.replay import Replay


class Master:
    def __init__(self, config, streams):
        self.config = config
        self.streams = streams
        
        self.chat = Chat(self.config['chat_conn_config'], self.streams)

        self.replays = {}

    def start_replay(self, logfile, stream, time_start):
        self.replays['stream'] = multiprocessing.Process(target=Replay,
                                                         args=(self.config['replay_config'],
                                                               logfile,
                                                               stream,
                                                               time_start))
        self.replays['stream'].start()
