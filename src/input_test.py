import zmq
import pickle

#import utils
from src.utils._functions_general import *
from src.chat.input.server import InputServer
from src.config.chat.input_config import input_config

input_server = InputServer(input_config)

# from src.sources.twitch.master import TwitchMaster
# from src.config.sources.twitch_config import twitch_config
# twitch_src = TwitchMaster(twitch_config)
# twitch_src.chat.join_stream('shroud')

# from src.sources.twitter.master import TwitterMaster
# from src.config.sources.twitter_config import twitter_config
# twitter_src = TwitterMaster(twitter_config)
# twitter_src.chat.join_stream('trump')

from src.sources.reddit.master import RedditMaster
from src.config.sources.reddit_config import reddit_config
reddit_src = RedditMaster(reddit_config)
reddit_src.chat.join_stream('soccer')

context = zmq.Context()
input_socket = context.socket(zmq.SUB)
input_socket.connect('tcp://'+'0.0.0.0'+':'+str(8030))
input_socket.connect('tcp://'+'0.0.0.0'+':'+str(8031))
input_socket.connect('tcp://'+'0.0.0.0'+':'+str(8032))
input_socket.connect('tcp://'+'0.0.0.0'+':'+str(8033))
input_socket.setsockopt(zmq.SUBSCRIBE, "")

for data in iter(input_socket.recv, '*STOP*'):
    #try: msg_data may be unpickleable?
    try:
        msg_data = pickle.loads(data)
        pp(msg_data)
    except Exception, e:
        pp(e)