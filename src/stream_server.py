# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""
import gc
import socket
import threading
import logging
import struct
import sys
import json
import time
import requests
import re
import copy
import pickle

logging.basicConfig()

from streams.twitch_stream import *
from streams.twitter_stream import *
from config.universal_config import *

import streams.utils.twtr as twtr_
from streams.utils.nlp import *

class StreamServer():
    def __init__(self, config):
        pp('Initializing Stream Server...')
        self.config = config
        self.init_sockets()

        self.twitch_streams = {}
        self.twitter_streams = {}

        self.twitch_featured = []
        self.twitter_featured = []

        #init twitter
        self.nlp_parser = nlpParser()
        self.twit = twtr_.twtr(twitter_config)
        

    def init_sockets(self):
        request_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        request_sock.bind((self.config['request_host'], self.config['request_port']))
        request_sock.listen(self.config['listeners'])
        self.request_sock = request_sock

        data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        data_sock.bind((self.config['data_host'], self.config['data_port']))
        data_sock.listen(self.config['listeners'])
        self.data_sock = data_sock

        self.sess = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.sess.mount('https://api.twitch.tv', adapter)

    #stream control
    def create_stream(self, stream, src):
        threading.Thread(target=self.add_stream, args=(stream,src)).start()

    def add_stream(self, stream, src):
        if src == 'twitch':
            self.twitch_streams[stream] = TwitchStream(twitch_config, stream)
            self.twitch_streams[stream].run()
        elif src == 'twitter':
            self.twitter_streams[stream] = TwitterStream(twitter_config, stream, self.twit, copy.copy(self.nlp_parser))
            self.twitter_streams[stream].run()
        else:
            pass

    def delete_stream(self, stream, src):
        if src == 'twitch':
            self.twitch_streams[stream].kill = True
            del self.twitch_streams[stream]
        elif src == 'twitter':
            self.twitter_streams[stream].kill = True
            del self.twitter_streams[stream]
            self.twit.leave_stream(stream)
        else:
            pass

    def get_stream_data(self):
        output = {}
        output['twitch_streams'] = {}
        output['twitter_streams'] = {}

        for stream in self.twitch_streams.keys():
            output['twitch_streams'][stream] = self.twitch_streams[stream].get_trending()

        for stream in self.twitter_streams.keys():
            output['twitter_streams'][stream] = self.twitter_streams[stream].get_trending()

        output['twitter_featured'] = self.twitter_featured
        output['twitch_featured'] = self.twitch_featured
        return pickle.dumps(output)

    def get_twitter_featured(self):
        try:
            trends = self.twit.hose_api.trends_place(23424977)
            output = [{'stream':x['name'],'description':x['name'],'count':x['tweet_volume']} for x in trends[0]['trends'] if x['tweet_volume']!=None]
            sorted_output = sorted(output, key=lambda k: k['count'], reverse=True) 

            self.twitter_featured = sorted_output
        except Exception, e:
            pp('Get Twitter featured failed.')
            pp(e)

    def get_twitch_featured(self):
        headers = {'Accept':'application/vnd.twitchtv.v3+json', 'Client-ID':self.config['twitch_client_id']}
        try:
            r = self.sess.get('https://api.twitch.tv/kraken/streams/featured', headers = headers)
            output = [{'stream':x['stream']['channel']['name'], 'image': x['stream']['preview']['medium'], 'description': x['title'], 'count': x['stream']['viewers']} for x in (json.loads(r.content))['featured']]
            sorted_output = sorted(output, key=lambda k: k['count'], reverse=True) 

            self.twitch_featured = sorted_output
        except Exception, e:
            pp('Get Twitch featured failed.')
            pp(e)
        
    def refresh_featured(self):
        self.refresh_loop = True
        while self.refresh_loop:
            self.get_twitch_featured()
            self.get_twitter_featured()

            time.sleep(300)

    def filter_twitch(self):
        self.filter_loop = True
        while self.filter_loop:
            if len(self.twitch_streams.keys()) > 0:
                for stream_key in self.twitch_streams.keys():
                    self.twitch_streams[stream_key].filter_trending()

            time.sleep(0.8)

    def render_twitch(self):
        self.clean_loop = True
        while self.clean_loop:
            if len(self.twitch_streams.keys()) > 0:
                for stream_key in self.twitch_streams.keys():
                    self.twitch_streams[stream_key].render_trending()

            time.sleep(0.17)

    def filter_twitter(self):
        self.filter_loop = True
        while self.filter_loop:
            if len(self.twitter_streams.keys()) > 0:
                for stream_key in self.twitter_streams.keys():
                    self.twitter_streams[stream_key].filter_trending()

            time.sleep(0.8)

    def render_twitter(self):
        self.clean_loop = True
        while self.clean_loop:
            if len(self.twitter_streams.keys()) > 0:
                for stream_key in self.twitter_streams.keys():
                    self.twitter_streams[stream_key].render_trending()

            time.sleep(0.17)

    def handle_http(self, client_sock, client_address):
        config = self.config
        connected = True

        while connected:
            data = client_sock.recv(config['socket_buffer_size']).rstrip()

            if len(data) == 0:
                pp(('Connection lost by: ' + str(client_address)))
                connected = False
            else:
                if config['debug']:
                    pp(data)

                jsondata = json.loads(data)

                if 'twitch' in jsondata:
                    if 'add' in jsondata['twitch']:
                        for stream in jsondata['twitch']['add']:
                            if stream not in self.twitch_streams:
                                self.create_stream(stream, 'twitch')

                    if 'delete' in jsondata['twitch']:
                        for stream in jsondata['twitch']['delete']:
                            if stream in self.twitch_streams:
                                self.delete_stream(stream, 'twitch')

                    if 'reset' in jsondata['twitch']:
                        for stream in self.twitch_streams:
                            self.twitch_streams[stream].kill = True
                            del self.twitch_streams[stream]

                if 'twitter' in jsondata:
                    if 'add' in jsondata['twitter']:
                        for stream in jsondata['twitter']['add']:
                            if stream not in self.twitter_streams:
                                self.create_stream(stream, 'twitter')

                    if 'delete' in jsondata['twitter']:
                        for stream in jsondata['twitter']['delete']:
                            if stream in self.twitter_streams:
                                self.delete_stream(stream, 'twitter')

                    if 'target_add' in jsondata['twitter']:
                        for stream in jsondata['twitter']['target_add']:
                            if stream not in self.twitter_streams:
                                twitter_config['target_streams'].append(stream)
                                self.create_stream(stream, 'twitter')

                    if 'refresh' in jsondata['twitter']:
                        self.twit.refresh_streams()

                    if 'reset' in jsondata['twitter']:
                        for stream in self.twitter_streams.keys():
                            self.twitter_streams[stream].kill = True
                            del self.twitter_streams[stream]
                        self.twit.reset_streams()  

    def listen(self):
        sock = self.request_sock
        config = self.config
        pp('Now listening...')
        self.listening = True

        while self.listening:
            (client_sock, client_address) = sock.accept()
            pp(('Request Connection initiated by: ' + str(client_address)))
            threading.Thread(target = self.handle_http, args = (client_sock,client_address)).start()

    def send_data(self, client_sock, client_address):
        connected = True

        while connected:
            pickle_data = self.get_stream_data()
            pickle_data = struct.pack('>I', len(pickle_data)) + pickle_data
            client_sock.sendall(pickle_data)

            time.sleep(0.17)

    def broadcast(self):
        sock = self.data_sock
        config = self.config
        pp('Now broadcasting...')
        self.broadcasting = True

        while self.broadcasting:
            (client_sock, client_address) = sock.accept()
            pp(('Broadcast Connection initiated by: ' + str(client_address)))
            threading.Thread(target = self.send_data, args = (client_sock,client_address)).start()

    def garbage_cleanup(self):
        gc.collect()
        time.sleep(300)

if __name__ == '__main__':
    #init
    server = StreamServer(server_config)
    #twitch helpers
    filter_twitch_thread = threading.Thread(target = server.filter_twitch).start()
    render_twitch_thread = threading.Thread(target = server.render_twitch).start()
    #twitter helpers
    filter_twitter_thread = threading.Thread(target = server.filter_twitter).start()
    render_twitter_thread = threading.Thread(target = server.render_twitter).start()
    #featured
    refresh_featured_thread = threading.Thread(target = server.refresh_featured).start()
    #serve
    listen_thread = threading.Thread(target = server.listen).start()
    broadcast_thread = threading.Thread(target = server.broadcast).start()
    #cleanup thread
    garbage_thread = threading.Thread(target = server.garbage_cleanup).start()
