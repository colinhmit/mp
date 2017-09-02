import multiprocessing

# import utils
from utils._functions_general import *
from utils.nlp import NLPParser
from input_internal import InternalInput
from input_twitch import TwitchInput
from input_twitter import TwitterInput
from input_reddit import RedditInput
from worker import InputWorker
from distributor import InputDistributor


class InputServer:
    def __init__(self, config):
        pp('Initializing Input Server...')
        self.config = config
        self.nlp_parser = NLPParser()

        if self.config['internal_on']:
            self.internal = InternalInput(self.config['internal_config'])
            multiprocessing.Process(target=InputDistributor,
                                    args=(self.config['internal_config'],)
                                    ).start()

        if self.config['twitch_on']:
            self.twitch = TwitchInput(self.config['twitch_config'])
            multiprocessing.Process(target=InputDistributor,
                                    args=(self.config['twitch_config'],)
                                    ).start()

        if self.config['twitter_on']:
            self.twitter = TwitterInput(self.config['twitter_config'])
            multiprocessing.Process(target=InputDistributor,
                                    args=(self.config['twitter_config'],)
                                    ).start()

        if self.config['reddit_on']:
            self.reddit = RedditInput(self.config['reddit_config'])
            multiprocessing.Process(target=InputDistributor,
                                    args=(self.config['reddit_config'],)
                                    ).start()

        for _ in xrange(self.config['num_workers']):
            multiprocessing.Process(target=InputWorker,
                                    args=(self.config['worker_config'],
                                          self.nlp_parser,)).start()
