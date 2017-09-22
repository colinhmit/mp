from src.config.socket_config import *

##############################################################################
# Worker
##############################################################################

worker_config = {
    # messaging
    'input_host': INPUT_HOST,
    'input_ports': {
        'internal':     INPUT_PORT_INTERNAL,
        'twitch':       INPUT_PORT_TWITCH,
        'twitter':      INPUT_PORT_TWITTER,
        'reddit':       INPUT_PORT_REDDIT
    },
    'dist_host': DIST_HOST,
    'dist_ports': {
        'internal':     DIST_PORT_INTERNAL,
        'twitch':       DIST_PORT_TWITCH,
        'twitter':      DIST_PORT_TWITTER,
        'reddit':       DIST_PORT_REDDIT
    },

    # parsers
    'modules': {
        'internal':     'src.sources.internal._functions_chat',
        'twitch':       'src.sources.twitch._functions_chat',
        'twitter':      'src.sources.twitter._functions_chat',
        'reddit':       'src.sources.reddit._functions_chat'
    }
}

##############################################################################
# Distributor
##############################################################################

from src.config.sources.internal_config import internal_config

from src.config.sources.twitch_config import twitch_config

from src.config.sources.twitter_config import twitter_config

from src.config.sources.reddit_config import reddit_config

dist_config = {
    'internal':     internal_config['chat_dist_config'],
    'twitch':       twitch_config['chat_dist_config'],
    'twitter':      twitter_config['chat_dist_config'],
    'reddit':       reddit_config['chat_dist_config']
}

##############################################################################
# Server
##############################################################################

input_config = {
    # worker setup
    'num_workers': 2,
    'worker_config': worker_config,

    # distributor setup
    'dist_config': dist_config
}