from src.utils._functions_general import *
from chat import TwitchChat

class TwitchMaster:
    def __init__(self, config):
        self.config = config
        self.streams = []
        
        self.chat = TwitchChat(self.config['chat_conn_config'], self.streams)
