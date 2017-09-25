#import utils
from src.utils._functions_general import *

# import chat
from src.procs.input_chat.master import InputChatMaster

class ProcServer:
    def __init__(self, config):
        pp('Initializing Proc Server...')
        self.config = config

        self.input_chat = InputChatMaster(self.config['input_chat_config'])

