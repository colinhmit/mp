from src.utils._functions_general import *
from chat import InternalChat

class InternalMaster:
    def __init__(self, config):
        self.config = config
        self.streams = []
        
        self.chat = InternalChat(self.config['chat'], self.streams)
