import socket
import threading
import time
import struct
import json
import zmq
import pickle
import datetime

from config.universal_config import server_config, input_config, stream_config, data_config, ad_config
from streams.utils.functions_general import *

from streams.native_manager import NativeManager
from streams.twitch_manager import TwitchManager
from streams.twitter_manager import TwitterManager
from streams.reddit_manager import RedditManager
from input_server import InputServer
from data_server import DataServer
from ad_server import AdServer

class StreamServer():
    def __init__(self, config, inputconfig, streamconfig, dataconfig, ad_config):
        pp('Initializing Stream Server...')
        self.config = config

        self.input_server = InputServer(inputconfig, self.config['init_streams'])

        self.native_manager = NativeManager(streamconfig)
        self.twitch_manager = TwitchManager(streamconfig, self.input_server.irc, self.config['init_streams']['twitch'])
        self.twitter_manager = TwitterManager(streamconfig, self.input_server.twtr, self.config['init_streams']['twitter'])
        self.reddit_manager = RedditManager(streamconfig, self.input_server.rddt, self.config['init_streams']['reddit'])
        
        #self.data_server = DataServer(dataconfig)

        self.ad_server = AdServer(ad_config)

        self.init_sockets()
        self.init_threads()
        
    def init_sockets(self):
        context = zmq.Context()
        self.server_socket = context.socket(zmq.PULL)
        self.server_socket.bind('tcp://'+self.config['zmq_server_host']+':'+str(self.config['zmq_server_port']))

    def init_threads(self):
        #serve
        threading.Thread(target = self.handle_http).start()

    def handle_http(self):
        self.http_connection = True
        while self.http_connection:
            raw_data = self.server_socket.recv()
            try:
                data = pickle.loads(raw_data)
                if 'native' in data:
                    if 'add' in data['native']:
                        for stream in data['native']['add']:
                            if (stream not in self.native_manager.streams) and (len(stream)>0):
                                self.native_manager.add_stream(stream)

                    if 'delete' in data['native']:
                        for stream in data['native']['delete']:
                            if stream in self.native_manager.streams:
                                self.native_manager.delete_stream(stream)

                if 'twitch' in data:
                    if 'add' in data['twitch']:
                        for stream in data['twitch']['add']:
                            if (stream not in self.twitch_manager.streams) and (len(stream)>0):
                                self.twitch_manager.add_stream(stream)

                    if 'delete' in data['twitch']:
                        for stream in data['twitch']['delete']:
                            if stream in self.twitch_manager.streams:
                                self.twitch_manager.delete_stream(stream)

                    if 'reset' in data['twitch']:
                        for stream in self.twitch_manager.streams.keys():
                            self.twitch_manager.delete_stream(stream)

                if 'twitter' in data:
                    # if 'add' in data['twitter']:
                    #     for stream in data['twitter']['add']:
                    #         if (stream not in self.twitter_manager.streams) and (len(stream)>0):
                    #             self.twitter_manager.add_stream(stream)

                    if 'delete' in data['twitter']:
                        for stream in data['twitter']['delete']:
                            if stream in self.twitter_manager.streams:
                                self.twitter_manager.delete_stream(stream)

                    if 'target_add' in data['twitter']:
                        for stream in data['twitter']['target_add']:
                            if (stream not in self.twitter_manager.streams) and (len(stream)>0):
                                self.twitter_manager.add_stream(stream)

                    if 'refresh' in data['twitter']:
                        self.input_server.twtr.refresh_streams()

                    if 'reset' in data['twitter']:
                        self.twitter_manager.featured = []
                        self.twitter_manager.featured_buffer = []
                        for stream in self.twitter_manager.streams.keys():
                            self.twitter_manager.streams[old_stream].terminate()
                            del self.twitter_manager.streams[old_stream]

                        self.input_server.twtr.reset_streams()  

                if 'reddit' in data:
                    if 'add' in data['reddit']:
                        for stream in data['reddit']['add']:
                            if (stream not in self.reddit_manager.streams) and (len(stream)>0):
                                self.reddit_manager.add_stream(stream)

                    if 'delete' in data['reddit']:
                        for stream in data['reddit']['delete']:
                            if stream in self.reddit_manager.streams:
                                self.reddit_manager.delete_stream(stream)

                    if 'refresh' in data['reddit']:
                        self.input_server.rddt.refresh_streams()

                    if 'reset' in data['reddit']:
                        for stream in self.reddit_manager.streams.keys():
                            self.reddit_manager.streams[old_stream].terminate()
                            del self.reddit_manager.streams[old_stream]

                        self.input_server.rddt.reset_streams() 

            except Exception, e:
                pp(e)

            
if __name__ == '__main__':
    #init
    server = StreamServer(server_config, input_config, stream_config, data_config, ad_config)