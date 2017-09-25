import zmq
import pickle
import threading

#import utils
from src.utils._functions_general import *
from src.inputs.chat.master import InputChatMaster
from src.config.inputs.input_chat_config import input_chat_config

from src.streams.chat.master import StreamChatMaster
from src.config.streams.stream_chat_config import stream_chat_config

from src.config.sources.internal_config import internal_config
from src.config.sources.twitch_config import twitch_config
from src.config.sources.reddit_config import reddit_config
from src.config.sources.twitter_config import twitter_config

input_server = InputChatMaster(input_chat_config)

streams = {}

# streams['shroud'] = {'chat': True}
# from src.sources.twitch.master import TwitchMaster
# from src.config.sources.twitch_config import twitch_config
# twitch_src = TwitchMaster(twitch_config, streams)
# twitch_src.chat.refresh_streams()
# stream_chat_config.update(twitch_config['stream_chat_config'])
# stream_chat_config['trending_config'].update(twitch_config['trending_config'])
# stream_chat_config['enrich_config'].update(twitch_config['enrich_config'])
# stream_chat_config['nlp_config'].update(twitch_config['nlp_config'])
# twitch_stream = StreamChatMaster(stream_chat_config, 'shroud')

# streams['trump'] = {'chat': True}
# from src.sources.twitter.master import TwitterMaster
# from src.config.sources.twitter_config import twitter_config
# twitter_src = TwitterMaster(twitter_config, streams)
# twitter_src.chat.refresh_streams()
# stream_chat_config.update(twitter_config['stream_chat_config'])
# stream_chat_config['trending_config'].update(twitter_config['trending_config'])
# stream_chat_config['enrich_config'].update(twitter_config['enrich_config'])
# stream_chat_config['nlp_config'].update(twitter_config['nlp_config'])
# twitter_stream = StreamChatMaster(stream_chat_config, 'trump')

streams['soccer'] = {'chat': True}
from src.sources.reddit.master import RedditMaster
from src.config.sources.reddit_config import reddit_config
reddit_src = RedditMaster(reddit_config, streams)
reddit_src.chat.refresh_streams()
stream_chat_config.update(reddit_config['stream_chat_config'])
stream_chat_config['trending_config'].update(reddit_config['trending_config'])
stream_chat_config['enrich_config'].update(reddit_config['enrich_config'])
stream_chat_config['nlp_config'].update(reddit_config['nlp_config'])
reddit_stream = StreamChatMaster(stream_chat_config, 'soccer')


