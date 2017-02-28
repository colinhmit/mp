from config.universal_config import *
from streams.twitter_stream import *
from streams.twitch_stream import *

# stream = TwitterStream(stream_config['twitter_config'],'trump')
# stream.run()

stream = TwitchStream(stream_config['twitch_config'],'esl_lol')
stream.run()