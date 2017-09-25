import praw

from src.utils._functions_general import *
from src.sources.reddit.chat import Chat


class Master:
    def __init__(self, config, streams):
        self.config = config
        self.streams = streams
        
        self.connect()
        self.chat = Chat(self.config['chat_conn_config'], self.streams, self.api)

    def connect(self):
        self.api = praw.Reddit(client_id=self.config['client_token'],
                               client_secret=self.config['client_secret'],
                               user_agent=self.config['user_agent'])