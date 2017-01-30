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

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

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
        self.twitter_api_featured = []
        self.twitter_manual_featured = []

        #twitter workarounds
        self.twitter_hash = None
        self.twitter_featured_buffer = []
        self.pattern = re.compile('[^\w\s\'\"!.,$&?:;_-]+')

        #init twitter
        self.target_twitter_streams = self.config['target_streams']

        self.nlp_parser = nlpParser()
        self.twit = twtr_.twtr(twitter_config, self.target_twitter_streams, self.nlp_parser)

        for stream in self.target_twitter_streams:
            self.create_stream(stream, 'twitter')
        
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

        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(self.config['sheets_key'], self.config['scopes'])
        self.service = build('sheets', 'v4', credentials=self.credentials)

    #stream control
    def create_stream(self, stream, src):
        threading.Thread(target=self.add_stream, args=(stream,src)).start()

    def add_stream(self, stream, src):
        if src == 'twitch':
            if stream not in self.twitch_streams:
                self.twitch_streams[stream] = TwitchStream(twitch_config, stream)
                self.twitch_streams[stream].run()
        elif src == 'twitter':
            if stream not in self.twitter_streams:
                self.twitter_streams[stream] = None 
                self.twit.join_stream(stream)
                self.twitter_streams[stream] = TwitterStream(twitter_config, stream, self.twit)
                self.twitter_streams[stream].run()

    def delete_stream(self, stream, src):
        if src == 'twitch':
            if stream in self.twitch_streams:
                try:
                    self.twitch_streams[stream].kill = True
                    del self.twitch_streams[stream]
                except Exception, e:
                    pp(e)
                    
        elif src == 'twitter':
            if stream in self.twitter_streams:
                try:
                    self.twitter_streams[stream].kill = True
                    del self.twitter_streams[stream]
                    self.twit.leave_stream(stream)
                except Exception, e:
                    pp(e)
     
    def get_stream_data(self):
        output = {}
        output['twitch_streams'] = {}
        output['twitter_streams'] = {}

        for stream in self.twitch_streams.keys():
            try:
                output['twitch_streams'][stream] = {}
                output['twitch_streams'][stream]['default_image'] = ''
                output['twitch_streams'][stream]['trending'] = self.twitch_streams[stream].get_trending()
            except Exception, e:
                pp(e)

        for stream in self.twitter_streams.keys():
            try:
                output['twitter_streams'][stream] = {}
                output['twitter_streams'][stream]['default_image'] = self.twitter_streams[stream].get_default_image()
                output['twitter_streams'][stream]['trending'] = self.twitter_streams[stream].get_trending()
            except Exception, e:
                pp(e)

        output['twitter_featured'] =  self.twitter_manual_featured + [dict(x, image=self.get_default_image_helper(x['stream'][0], 'twitter')) for x in self.twitter_api_featured]
        output['twitch_featured'] = self.twitch_featured
        output['target_twitter_streams'] = self.target_twitter_streams
        return pickle.dumps(output)

    def get_default_image_helper(self, stream, src):
        default_image = ''
        if src == 'twitter':
            try:
                default_image = self.twitter_streams[stream].get_default_image()
            except Exception, e:
                pp('get image failing')
                pp(e)

        return default_image

    def get_twitter_featured(self):
        try:
            trends = self.twit.api.trends_place(23424977)
            output = [{'title':x['name'],'stream':[self.pattern.sub('',x['name']).lower()],'description':'','count':x['tweet_volume']} for x in trends[0]['trends'] if x['tweet_volume']!=None]
            sorted_output = sorted(output, key=lambda k: k['count'], reverse=True) 
            sorted_output = sorted_output[0:self.config['twitter_num_featured']]

            streams_to_add = [x['stream'][0] for x in sorted_output]
            streams_to_remove = []

            self.twitter_featured_buffer += streams_to_add

            while len(self.twitter_featured_buffer)>100:
                old_stream = self.twitter_featured_buffer.pop(0)
                if (old_stream not in self.twitter_featured_buffer) and (old_stream in self.twitter_streams):
                    try:
                        self.twitter_streams[old_stream].kill = True
                        del self.twitter_streams[old_stream]
                    except Exception, e:
                        pp(e)
                    streams_to_remove.append(old_stream)

            self.twit.batch_streams(streams_to_add, streams_to_remove)

            for featured_stream in streams_to_add:
                self.create_stream(featured_stream, 'twitter')

            self.twitter_api_featured = sorted_output

        except Exception, e:
            pp('Get Twitter API featured failed.')
            pp(e)

    def get_twitter_featured_manual(self):
        try:
            result = self.service.spreadsheets().values().get(spreadsheetId=self.config['spreadsheetID'], range=self.config['featured_live_range']).execute()
            values = result.get('values', [])
            live_bool = int(values[0][0])

            if live_bool == 1:
                result = self.service.spreadsheets().values().get(spreadsheetId=self.config['spreadsheetID'], range=self.config['featured_data_range']).execute()
                values = result.get('values', [])

                manual_featured = []
                for row in values:
                    manual_featured.append({'title':row[0], 'stream':row[1].split(","), 'image':row[3], 'description':row[2], 'count':row[4]})

                if manual_featured != self.twitter_manual_featured:
                    current_manual_streams = [x['stream'] for x in self.twitter_manual_featured]
                    current_manual_streams = [val for sublist in current_manual_streams for val in sublist]

                    addition_manual_streams = [x['stream'] for x in manual_featured]
                    addition_manual_streams = [val for sublist in addition_manual_streams for val in sublist]

                    for old_stream in current_manual_streams:
                        if (old_stream not in addition_manual_streams) and (old_stream in self.twitter_streams):
                            try:
                                self.twitter_streams[old_stream].kill = True
                                del self.twitter_streams[old_stream]
                            except Exception, e:
                                pp(e)

                    self.twit.batch_streams(addition_manual_streams, current_manual_streams)

                    for featured_stream in addition_manual_streams:
                        self.create_stream(featured_stream, 'twitter')

                    self.twitter_manual_featured = manual_featured

        except Exception, e:
            pp('Get Twitter manual featured failed.')
            pp(e)

    def get_twitch_featured(self):
        headers = {'Accept':'application/vnd.twitchtv.v3+json', 'Client-ID':self.config['twitch_client_id']}
        try:
            r = self.sess.get('https://api.twitch.tv/kraken/streams', headers = headers)
            output = [{'title':x['channel']['name'], 'stream':x['channel']['name'], 'image': x['preview']['medium'], 'description': x['channel']['status'], 'game': x['game'], 'count': x['viewers']} for x in (json.loads(r.content))['streams']]
            sorted_output = sorted(output, key=lambda k: k['count'], reverse=True) 
            self.twitch_featured = sorted_output[0:self.config['twitch_num_featured']]
        except Exception, e:
            pp('Get Twitch featured failed.')
            pp(e)
        
    def refresh_featured(self):
        self.refresh_loop = True
        while self.refresh_loop:
            self.get_twitch_featured()
            self.get_twitter_featured()

            time.sleep(1200)

    def refresh_manual(self):
        self.refresh_manual = True
        while self.refresh_manual:
            self.get_twitter_featured_manual()

            time.sleep(60)

    def filter_twitch(self):
        self.filter_loop = True
        while self.filter_loop:
            if len(self.twitch_streams.keys()) > 0:
                for stream_key in self.twitch_streams.keys():
                    try:
                        self.twitch_streams[stream_key].filter_trending()
                    except Exception, e:
                        pp(e)
                    
            time.sleep(0.8)

    def render_twitch(self):
        self.clean_loop = True
        while self.clean_loop:
            if len(self.twitch_streams.keys()) > 0:
                for stream_key in self.twitch_streams.keys():
                    try:
                        self.twitch_streams[stream_key].render_trending()
                    except Exception, e:
                        pp(e)

            time.sleep(0.3)

    def filter_twitter(self):
        self.filter_loop = True
        while self.filter_loop:
            if len(self.twitter_streams.keys()) > 0:
                for stream_key in self.twitter_streams.keys():
                    try:
                        self.twitter_streams[stream_key].filter_trending()
                    except Exception, e:
                        pp(e)

            time.sleep(0.8)

    def render_twitter(self):
        self.clean_loop = True
        while self.clean_loop:
            if len(self.twitter_streams.keys()) > 0:
                for stream_key in self.twitter_streams.keys():
                    try:
                        self.twitter_streams[stream_key].render_trending()
                    except Exception, e:
                        pp(e)

            time.sleep(0.3)

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
                            #CURRENTLY BLOCKING NON TARGET
                            if (stream not in self.twitter_streams) and (len(stream)>0) and (stream in self.target_twitter_streams):
                                self.create_stream(stream, 'twitter')

                    if 'delete' in jsondata['twitter']:
                        for stream in jsondata['twitter']['delete']:
                            if stream in self.twitter_streams:
                                self.delete_stream(stream, 'twitter')

                    if 'target_add' in jsondata['twitter']:
                        for stream in jsondata['twitter']['target_add']:
                            if (stream not in self.twitter_streams) and (len(stream)>0):
                                self.target_twitter_streams.append(stream)
                                self.create_stream(stream, 'twitter')

                    if 'refresh' in jsondata['twitter']:
                        self.twit.refresh_streams()

                    if 'reset' in jsondata['twitter']:
                        self.twitter_featured = []
                        self.twitter_featured_buffer = []
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

            time.sleep(0.3)

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

    def monitor_twitter(self):
        monitor = True

        while monitor:
            curr_dict = {}

            for stream in self.twitter_streams.values():
                try:
                    curr_dict.update(stream.get_trending())
                except Exception, e:
                    pp(e)

            curr_hash = hash(frozenset(curr_dict))
            if curr_hash == self.twitter_hash:
                pp('Monitor twitter triggered - refreshing!')
                self.twit.refresh_streams()
            else:
                self.twitter_hash = curr_hash

            time.sleep(15)

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
    #Google API
    manual_thread = threading.Thread(target = server.refresh_manual).start()
    #serve
    listen_thread = threading.Thread(target = server.listen).start()
    broadcast_thread = threading.Thread(target = server.broadcast).start()
    #cleanup thread
    garbage_thread = threading.Thread(target = server.garbage_cleanup).start()
    monitor_thread = threading.Thread(target = server.monitor_twitter).start()
