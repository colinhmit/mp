import zmq
import pickle
import threading

#import utils
from src.utils._functions_general import *
from src.inputs.chat.master import InputChatMaster
from src.config.inputs.chat_config import input_chat_config

input_server = InputChatMaster(input_chat_config)

streams = {}

# from src.sources.twitch.master import TwitchMaster
# from src.config.sources.twitch_config import twitch_config
# twitch_src = TwitchMaster(twitch_config, streams)
# #twitch_src.chat.join_stream('shroud')
# #twitch_src.chat.refresh_streams()
# streams['shroud'] = {'chat': True}

# from src.sources.twitter.master import TwitterMaster
# from src.config.sources.twitter_config import twitter_config
# twitter_src = TwitterMaster(twitter_config, streams)
# twitter_src.chat.join_stream('trump')
# twitter_src.chat.refresh_streams()
# streams['trump'] = {'chat': True}

from src.sources.reddit.master import RedditMaster
from src.config.sources.reddit_config import reddit_config
reddit_src = RedditMaster(reddit_config, streams)
# reddit_src.chat.join_stream('soccer')
#reddit_src.chat.refresh_streams()
streams['soccer'] = {'chat': True}

output=[]
def get_inputs():
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
            output.append(msg_data)
        except Exception, e:
            pp(e)

threading.Thread(target=get_inputs).start()


