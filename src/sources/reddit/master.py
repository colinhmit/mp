import praw

from src.utils._functions_general import *
from chat import RedditChat

class RedditMaster:
    def __init__(self, config):
        self.config = config
        self.streams = []
        
        self.chat = RedditChat(self.config['chat'], self.streams, self.api)

    def connect(self):
        self.api = praw.Reddit(client_id=self.config['client_token'],
                               client_secret=self.config['client_secret'],
                               user_agent=self.config['user_agent'])