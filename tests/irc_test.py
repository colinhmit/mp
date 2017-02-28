import input_server as input_server_
import streams.stream_manager as stream_manager_

from config.universal_config import *

server = input_server_.InputServer(input_config,stream_config['target_streams'])
mgr = stream_manager_.StreamManager(stream_config,server.irc,server.twtr)
mgr.create_stream('tsm_dyrus', 'twitch')
mgr.create_stream('esl_lol', 'twitch')
