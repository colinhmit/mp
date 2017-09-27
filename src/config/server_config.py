from src.config.sources.internal_config import internal_config
from src.config.sources.twitch_config import twitch_config
from src.config.sources.twitter_config import twitter_config
from src.config.sources.reddit_config import reddit_config

from src.config.procs.proc_config import proc_config

from src.config.streams.stream_config import stream_config

##############################################################################
# Server
##############################################################################

server_config = {
    # on?
    'src_on': {
        'internal':     False,
        'twitch':       True,
        'twitter':      False,
        'reddit':       False
    },

    # modules
    'src_modules': {
        'internal':     'src.sources.internal.master',
        'twitch':       'src.sources.twitch.master',
        'twitter':      'src.sources.twitter.master',
        'reddit':       'src.sources.reddit.master'
    },

    # configs
    'src_configs': {
        'internal':     internal_config,
        'twitch':       twitch_config,
        'twitter':      twitter_config,
        'reddit':       reddit_config,
    },
    'proc_config': proc_config,
    'stream_config': stream_config
}