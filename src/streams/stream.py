#import utils
from src.utils._functions_general import *
from src.streams.chat.master import StreamChatMaster


class Stream:
    def __init__(self, config, src_config, stream):
        self.set_config(config, src_config)
        self.stream = stream

        self.chat = StreamChatMaster(self.config['stream_chat_config'], self.stream)

    def set_config(self, config, src_config):
        config['stream_chat_config'].update(src_config['stream_chat_config'])
        config['stream_chat_config']['trending_config'].update(src_config['trending_config'])
        config['stream_chat_config']['nlp_config'].update(src_config['nlp_config'])
        self.config = config
