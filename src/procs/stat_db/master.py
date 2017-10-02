import multiprocessing

# import utils
from src.utils._functions_general import *
from src.procs.stat_db.chat_velocity_stats import ChatVelocityStats
from src.procs.stat_db.chat_sentiment_stats import ChatSentimentStats


class StatDBMaster:
    def __init__(self, config):
        pp('Initializing Stat DB Master...')
        self.config = config

        self.chat_velocity_stats = ChatVelocityStats(self.config['chat_velocity_config'])
        self.chat_sentiment_stats = ChatSentimentStats(self.config['chat_sentiment_config'])
