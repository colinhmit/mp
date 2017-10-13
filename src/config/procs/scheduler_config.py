from src.config.sources.internal_config import internal_config
from src.config.sources.twitch_config import twitch_config
from src.config.sources.twitter_config import twitter_config
from src.config.sources.reddit_config import reddit_config
from src.config.streams.stream_config import stream_config

scheduler_config = {
    # AWS Google API Key
    'sheets_key': '/home/ec2-user/mp/src/config/keys/sheets_key.json',
    # DEV Google API Key
    #'sheets_key': '/Users/colinh/Repositories/mp/src/config/keys/sheets_key.json',
    
    # credentials
    'scopes': ['https://www.googleapis.com/auth/spreadsheets.readonly'],
    'spreadsheetID': '1lz4g3-WvT8EjVc2hogalhnGQmkMb1d1fIvatpLUsano',
    
    # range
    'live_range': 'Schedule!J2',
    'data_range': 'Schedule!A2:H',

    # configs
    'src_configs': {
        'internal':     internal_config,
        'twitch':       twitch_config,
        'twitter':      twitter_config,
        'reddit':       reddit_config,
    },
    'stream_config': stream_config,

    # timezon
    'timezone': 'EST',
    # timing
    'get_schedule_refresh': 60,
    'set_streams_refresh': 1
}
