from tweepy import OAuthHandler
from tweepy import API

from src.utils._functions_general import *
from src.sources.twitter.chat import Chat


class Master:
    def __init__(self, config, streams):
        self.config = config
        self.streams = streams

        self.connect()
        self.chat = Chat(self.config['chat_conn_config'], self.streams, self.auth)

    def connect(self):
        self.auth = OAuthHandler(self.config['consumer_token'], self.config['consumer_secret'])
        self.auth.set_access_token(self.config['access_token'], self.config['access_secret'])
        self.api = API(self.auth)
