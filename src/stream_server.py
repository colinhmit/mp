# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""

import socket
import threading
import logging
import sys
import json
import time
import requests
import re

logging.basicConfig()

from streams.twitch_stream import *
from streams.twitter_stream import *
from config.universal_config import *

import streams.utils.twtr as twtr_

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
        self.twit = twtr_.twtr(twitter_config)

        #CJK regex
        self.pattern = re.compile('[^\w\s_]+')

    def init_sockets(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind((self.config['listen_host'], self.config['listen_port']))
        sock.listen(self.config['listeners'])
        self.listen_socket = sock

        multisock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        multisock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.config['ttl'])
        self.multi_socket = multisock

    #stream control
    def create_stream(self, stream, src):
        threading.Thread(target=self.add_stream, args=(stream,src)).start()

    def add_stream(self, stream, src):
        if src == 'twitch':
            self.twitch_streams[stream] = TwitchStream(twitch_config, stream)
            self.twitch_streams[stream].run()
        elif src == 'twitter':
            self.twitter_streams[stream] = TwitterStream(twitter_config, stream, self.twit)
            self.twitter_streams[stream].run()
        else:
            pass

    def delete_stream(self, stream, src):
        if src == 'twitch':
            self.twitch_streams[stream].kill = True
            del self.twitch_streams[stream]
        elif src == 'twitter':
            self.twitter_streams[channel].kill = True
            del self.twitter_streams[channel]
            self.twit.leave_channel(channel)
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
        return json.dumps(output)

    def get_twitter_featured(self):
        pp('Getting twitter featured...')
        trends = self.twit.hose_api.trends_place(1)
        output = [{'stream':x['name'],'description':x['name'],'count':x['tweet_volume']} for x in trends[0]['trends'] if x['tweet_volume']!=None]
        sorted_output = sorted(output, key=lambda k: k['count'], reverse=True) 

        self.twitter_featured = sorted_output

    def get_twitch_featured(self):
        headers = {'Accept':'application/vnd.twitchtv.v3+json', 'Client-ID':self.config['twitch_client_id']}
        r = requests.get('https://api.twitch.tv/kraken/streams/featured', headers = headers)
        output = [{'stream':x['stream']['channel']['name'], 'image': x['stream']['preview']['medium'], 'description': x['title'], 'count': x['stream']['viewers']} for x in (json.loads(r.content))['featured']]
        sorted_output = sorted(output, key=lambda k: k['count'], reverse=True) 

        self.twitch_featured = sorted_output

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

    def multicast(self):
        multisock = self.multi_socket
        config = self.config
        pp('Now multicasting...')
        self.multicast = True

        while self.multicast:
            json_data = self.get_stream_data()
            pp(json.loads(json_data)['twitch_streams'])
            multisock.sendto(json_data, (self.config['multicast_server'],self.config['multicast_port']))
            time.sleep(0.17)

    def listen_to_http(self, client_sock, client_address):
        config = self.config
        connected = True

        while connected:
            data = client_sock.recv(config['socket_buffer_size']).rstrip()

            if len(data) == 0:
                pp(('Connection lost by: ' + str(client_address)))
                connected = False

            if config['debug']:
                pp(data)

            jsondata = json.loads(data)

            if 'twitch' in jsondata.keys():
                if 'add' in jsondata['twitch'].keys():
                    for stream in jsondata['twitch']['add']:
                        if stream not in self.twitch_streams.keys():
                            self.create_stream(stream, 'twitch')

                if 'delete' in jsondata['twitch'].keys():
                    for stream in jsondata['twitch']['delete']:
                        if stream in self.twitch_streams.keys():
                            self.delete_stream(stream, 'twitch')

            if 'twitter' in jsondata.keys():
                if 'add' in jsondata['twitter'].keys():
                    for stream in jsondata['twitter']['add']:
                        if stream not in self.twitter_streams.keys():
                            self.create_stream(stream, 'twitter')

                if 'delete' in jsondata['twitter'].keys():
                    for stream in jsondata['twitter']['delete']:
                        if stream in self.twitter_streams.keys():
                            self.delete_stream(stream, 'twitter')

                if 'target_add' in jsondata['twitter'].keys():
                    for stream in jsondata['twitter']['target_add']:
                        if stream not in self.twitter_streams.keys():
                            twitter_config['target_streams'].append(channel)
                            self.create_stream(stream, 'twitter')

    def listen(self):
        sock = self.listen_socket
        config = self.config
        pp('Now listening...')
        self.listening = True

        while self.listening:
            (client_sock, client_address) = sock.accept()
            pp(('Connection initiated by: ' + str(client_address)))
            threading.Thread(target = self.listen_to_http,args = (client_sock,client_address)).start()

if __name__ == '__main__':
    #init
    server = StreamServer(server_config)
    #twitch helpers
    filter_twitch_thread = threading.Thread(target = server.filter_twitch).start()
    render_twitch_thread = threading.Thread(target = server.render_twitch).start()
    #twitter helpers
    filter_twitter_thread = threading.Thread(target = server.filter_twitter).start()
    render_twitter_thread = threading.Thread(target = server.render_twitter).start()
    #serve
    server.get_twitter_featured()
    server.get_twitch_featured()

    listen_thread = threading.Thread(target = server.listen).start()
    multicast_thread = threading.Thread(target = server.multicast).start()
