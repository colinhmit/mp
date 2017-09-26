#import utils
from src.utils._functions_general import *

# import chat
from src.procs.input_chat.master import InputChatMaster

# import forwarder
from src.procs.forwarder.forwarder import Forwarder

# import inputdb
from src.procs.input_db.master import InputDBMaster

class ProcServer:
    def __init__(self, config):
        pp('Initializing Proc Server...')
        self.config = config

        self.input_chat = InputChatMaster(self.config['input_chat_config'])

        self.forwarder = Forwarder(self.config['forwarder_config'])

        self.input_db = InputDBMaster(self.config['input_db_config'])

