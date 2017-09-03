import multiprocessing

# import utils
from utils._functions_general import *
from utils.nlp import NLPParser
from input_internal import InputInternal
from input_twitch import InputTwitch
from input_twitter import InputTwitter
from input_reddit import InputReddit
from worker import InputWorker
from distributor import InputDistributor


class InputServer:
    def __init__(self, config):
        pp('Initializing Input Server...')
        self.config = config
        self.nlp_parser = NLPParser()

        if self.config['internal_on']:
            self.internal = InputInternal(self.config['internal_config'])
            multiprocessing.Process(target=InputDistributor,
                                    args=(self.config['internal_config'],)
                                    ).start()

        if self.config['twitch_on']:
            self.twitch = InputTwitch(self.config['twitch_config'])
            multiprocessing.Process(target=InputDistributor,
                                    args=(self.config['twitch_config'],)
                                    ).start()

        if self.config['twitter_on']:
            self.twitter = InputTwitter(self.config['twitter_config'])
            multiprocessing.Process(target=InputDistributor,
                                    args=(self.config['twitter_config'],)
                                    ).start()

        if self.config['reddit_on']:
            self.reddit = InputReddit(self.config['reddit_config'])
            multiprocessing.Process(target=InputDistributor,
                                    args=(self.config['reddit_config'],)
                                    ).start()

        for _ in xrange(self.config['num_workers']):
            multiprocessing.Process(target=InputWorker,
                                    args=(self.config['worker_config'],
                                          self.nlp_parser,)).start()
