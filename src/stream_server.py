# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""
import socket
import threading
import time
import re
import struct
import json
import pickle
import datetime
import gc

from config.universal_config import *
from streams.utils.functions_general import *

from streams.stream_manager import StreamManager
from input_server import InputServer
from data_server import DataServer

class StreamServer():
    def __init__(self, config, inputconfig, streamconfig, dataconfig):
        pp('Initializing Stream Server...')
        self.config = config
        self.pattern = re.compile('[^\w\s\'\"!.,$&?:;_-]+')

        #init twitter
        self.target_twitter_streams = self.config['init_twitter_streams']

        self.input_server = InputServer(inputconfig, self.target_twitter_streams)
        self.stream_manager = StreamManager(streamconfig, self.input_server.irc, self.input_server.twtr, self.target_twitter_streams)
        #self.data_server = DataServer(dataconfig)

        self.init_sockets()
        self.init_threads()
        
    def init_sockets(self):
        request_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        request_sock.bind((self.config['request_host'], self.config['request_port']))
        request_sock.listen(self.config['listeners'])
        self.request_sock = request_sock

        twitch_data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        twitch_data_sock.bind((self.config['data_host'], self.config['twitch_data_port']))
        twitch_data_sock.listen(self.config['listeners'])
        self.twitch_data_sock = twitch_data_sock

        twitter_data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        twitter_data_sock.bind((self.config['data_host'], self.config['twitter_data_port']))
        twitter_data_sock.listen(self.config['listeners'])
        self.twitter_data_sock = twitter_data_sock

        featured_data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        featured_data_sock.bind((self.config['data_host'], self.config['featured_data_port']))
        featured_data_sock.listen(self.config['listeners'])
        self.featured_data_sock = featured_data_sock

        analytics_data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        analytics_data_sock.bind((self.config['data_host'], self.config['analytics_data_port']))
        analytics_data_sock.listen(self.config['listeners'])
        self.analytics_data_sock = analytics_data_sock

    def init_threads(self):
         #serve
        listen_thread = threading.Thread(target = self.listen).start()
        broadcast_twitch_thread = threading.Thread(target = self.broadcast, args = ('twitch',)).start()
        broadcast_twitter_thread = threading.Thread(target = self.broadcast, args = ('twitter',)).start()
        broadcast_featured_thread = threading.Thread(target = self.broadcast, args = ('featured',)).start()
        broadcast_analytics_thread = threading.Thread(target = self.broadcast, args = ('analytics',)).start()
        
    def get_stream_data(self, src):
        output = {}

        if src == 'twitch':
            output['twitch_streams'] = {}
            for stream in self.stream_manager.twitch_streams.keys():
                try:
                    output['twitch_streams'][stream] = {}
                    output['twitch_streams'][stream]['default_image'] = ''
                    output['twitch_streams'][stream]['trending'] = self.stream_manager.twitch_streams[stream].get_trending()
                except Exception, e:
                    pp(e)

        elif src == 'twitter':
            output['twitter_streams'] = {}
            for stream in self.stream_manager.twitter_streams.keys():
                try:
                    output['twitter_streams'][stream] = {}
                    output['twitter_streams'][stream]['default_image'] = self.stream_manager.twitter_streams[stream].get_default_image()
                    output['twitter_streams'][stream]['trending'] = self.stream_manager.twitter_streams[stream].get_trending()
                    output['twitter_streams'][stream]['content'] = self.stream_manager.twitter_streams[stream].get_content()
                except Exception, e:
                    pp(e)

        elif src == 'featured':
            output['twitter_featured'] =  self.stream_manager.twitter_manual_featured + [dict(x, image=self.get_default_image_helper(x['stream'][0], 'twitter')) for x in self.stream_manager.twitter_api_featured]
            output['twitch_featured'] = self.stream_manager.twitch_api_featured
            output['target_twitter_streams'] = self.target_twitter_streams

        elif src == 'analytics':
            output['analytics'] = {}
            for stream in self.stream_manager.twitter_streams.keys():
                try:
                    output['analytics'][stream] = {}
                    output['analytics'][stream]['clusters'] = self.stream_manager.twitter_streams[stream].get_clusters()
                except Exception, e:
                    pp(e)

        return pickle.dumps(output)

    def get_default_image_helper(self, stream, src):
        default_image = ''
        if src == 'twitter':
            try:
                default_image = self.stream_manager.twitter_streams[stream].get_default_image()
            except Exception, e:
                pp('get image failing')
                pp(e)

        return default_image

    def handle_http(self, client_sock, client_address):
        connected = True

        while connected:
            data = client_sock.recv(self.config['socket_buffer_size']).rstrip()

            if len(data) == 0:
                pp(('Connection lost by: ' + str(client_address)))
                connected = False
            else:
                jsondata = json.loads(data)

                if 'twitch' in jsondata:
                    if 'add' in jsondata['twitch']:
                        for stream in jsondata['twitch']['add']:
                            if stream not in self.stream_manager.twitch_streams:
                                self.stream_manager.create_stream(stream, 'twitch')

                    if 'delete' in jsondata['twitch']:
                        for stream in jsondata['twitch']['delete']:
                            if stream in self.stream_manager.twitch_streams:
                                self.stream_manager.delete_stream(stream, 'twitch')

                    if 'reset' in jsondata['twitch']:
                        for stream in self.stream_manager.twitch_streams:
                            self.stream_manager.twitch_streams[stream].kill = True
                            del self.stream_manager.twitch_streams[stream]

                if 'twitter' in jsondata:
                    if 'add' in jsondata['twitter']:
                        for stream in jsondata['twitter']['add']:
                            #CURRENTLY BLOCKING NON TARGET
                            if (stream not in self.stream_manager.twitter_streams) and (len(stream)>0) and (stream in self.target_twitter_streams):
                                self.stream_manager.create_stream(stream, 'twitter')

                    if 'delete' in jsondata['twitter']:
                        for stream in jsondata['twitter']['delete']:
                            if stream in self.stream_manager.twitter_streams:
                                self.stream_manager.delete_stream(stream, 'twitter')

                    if 'target_add' in jsondata['twitter']:
                        for stream in jsondata['twitter']['target_add']:
                            if (stream not in self.stream_manager.twitter_streams) and (len(stream)>0):
                                self.target_twitter_streams.append(stream)
                                self.stream_manager.create_stream(stream, 'twitter')

                    if 'refresh' in jsondata['twitter']:
                        self.input_server.twtr.refresh_streams()

                    if 'reset' in jsondata['twitter']:
                        self.stream_manager.twitter_featured = []
                        self.stream_manager.twitter_featured_buffer = []
                        for stream in self.stream_manager.twitter_streams.keys():
                            self.stream_manager.twitter_streams[stream].kill = True
                            del self.stream_manager.twitter_streams[stream]

                        self.input_server.twtr.reset_streams()  

    def listen(self):
        sock = self.request_sock
        config = self.config
        pp('Now listening...')
        listening = True

        while listening:
            try:
                (client_sock, client_address) = sock.accept()
                pp(('Request Connection initiated by: ' + str(client_address)))
                threading.Thread(target = self.handle_http, args = (client_sock,client_address)).start()
            except Exception, e:
                pp(e)
            
    def send_data(self, client_sock, client_address, src):
        timeout = 100000
        if src == 'twitch':
            timeout = 0.3
        elif src == 'twitter':
            timeout = 0.7
        elif src == 'featured':
            timeout = 1200
        elif src == 'analytics':
            timeout = 60

        connected = True
        while connected:
            pickle_data = self.get_stream_data(src)
            pickle_data = struct.pack('>I', len(pickle_data)) + pickle_data
            client_sock.sendall(pickle_data)

            time.sleep(timeout)

    def broadcast(self, src):
        sock = None
        if src == 'twitch':
            sock = self.twitch_data_sock
        elif src == 'twitter':
            sock = self.twitter_data_sock
        elif src == 'featured':
            sock = self.featured_data_sock
        elif src == 'analytics':
            sock = self.analytics_data_sock

        pp('Now broadcasting for: ' + src + '...')
        broadcasting = True

        while broadcasting:
            try:
                (client_sock, client_address) = sock.accept()
                pp(('Broadcast Connection initiated by: ' + str(client_address)))
                threading.Thread(target = self.send_data, args = (client_sock,client_address,src)).start()
            except Exception, e:
                pp(e)
                
if __name__ == '__main__':
    #init
    server = StreamServer(server_config, input_config, stream_config, data_config)