from tweepy import OAuthHandler
from tweepy import API

from src.utils._functions_general import *
from chat import TwitterChat

class TwitterMaster:
    def __init__(self, config):
        self.config = config
        self.streams = []

        self.connect()
        self.chat = TwitterChat(self.config['chat_conn_config'], self.streams, self.auth)

    def connect(self):
        self.auth = OAuthHandler(self.config['consumer_token'], self.config['consumer_secret'])
        self.auth.set_access_token(self.config['access_token'], self.config['access_secret'])
        self.api = API(self.auth)
