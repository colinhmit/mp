from src.utils._functions_general import *
from src.sources.twitch.chat import Chat


class Master:
    def __init__(self, config, streams):
        self.config = config
        self.streams = streams
        
        self.chat = Chat(self.config['chat_conn_config'], self.streams)
