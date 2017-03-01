# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""
import re
import gc
import threading
import json
import time
import zmq
import requests
import datetime
import pickle

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

from utils.functions_general import *
from twitch_stream import TwitchStream
from twitter_stream import TwitterStream

class StreamManager():
    def __init__(self, config, irc, twtr, init_twitter_streams):
        pp('Initializing Stream Manager...')
        self.config = config
        self.twitch_streams = {}
        self.twitter_streams = {}

        self.twitch_api_featured = []
        self.twitter_api_featured = []
        self.twitter_manual_featured = []
        self.twitter_featured_buffer = []

        self.schedule = []

        #Twitter Monitor
        self.twitter_hash = None
    
        self.pattern = re.compile('[^\w\s\'\"!.,$&?:;_-]+')

        self.irc = irc
        self.twtr = twtr
        self.init_sockets()

        for stream in init_twitter_streams:
            self.create_stream(stream, 'twitter')

        self.init_threads()

    def init_sockets(self):
        self.sess = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.sess.mount('https://api.twitch.tv', adapter)

        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(self.config['sheets_key'], self.config['scopes'])
        self.service = build('sheets', 'v4', credentials=self.credentials)

        context = zmq.Context()
        self.subj_sock = context.socket(zmq.PUB)
        self.subj_sock.bind("tcp://127.0.0.1:"+str(self.config['zmq_subj_port']))

        self.cluster_sock = context.socket(zmq.SUB)
        self.cluster_sock.bind("tcp://127.0.0.1:"+str(self.config['zmq_cluster_port']))
        self.cluster_sock.setsockopt(zmq.SUBSCRIBE, "")

    def init_threads(self):
        #twitch helpers
        filter_trending_twitch_thread = threading.Thread(target = self.filter_trending_twitch).start()
        render_twitch_thread = threading.Thread(target = self.render_twitch).start()

        #twitter helpers
        filter_trending_twitter_thread = threading.Thread(target = self.filter_trending_twitter).start()
        filter_content_twitter_thread = threading.Thread(target = self.filter_content_twitter).start()
        render_twitter_thread = threading.Thread(target = self.render_twitter).start()
    
        #featured
        refresh_featured_thread = threading.Thread(target = self.refresh_featured).start()
    
        #logging
        #logging_thread = threading.Thread(target = self.log_monitor).start()
    
        #subj suggestions
        #reset_subj_twitch_thread = threading.Thread(target = self.reset_subjs_twitch).start()
        #reset_subj_twitter_thread = threading.Thread(target = self.reset_subjs_twitter).start()
        #subj_thread = threading.Thread(target = self.send_subjs).start()
        #cluster_thread = threading.Thread(target = self.recv_clusters).start()
   
        #cleanup thread
        garbage_thread = threading.Thread(target = self.garbage_cleanup).start()
        monitor_thread = threading.Thread(target = self.monitor_twitter).start()

    #stream control
    def create_stream(self, stream, src):
        threading.Thread(target=self.add_stream, args=(stream,src)).start()

    def add_stream(self, stream, src):
        if src == 'twitch':
            if stream not in self.twitch_streams:
                self.twitch_streams[stream] = None 
                self.irc.join_stream(stream)
                self.twitch_streams[stream] = TwitchStream(self.config['twitch_config'], stream)
                self.twitch_streams[stream].run()
        elif src == 'twitter':
            if stream not in self.twitter_streams:
                self.twitter_streams[stream] = None 
                self.twtr.join_stream(stream)
                self.twitter_streams[stream] = TwitterStream(self.config['twitter_config'], stream)
                self.twitter_streams[stream].run()

    def delete_stream(self, stream, src):
        if src == 'twitch':
            if stream in self.twitch_streams:
                try:
                    self.twitch_streams[stream].kill = True
                    del self.twitch_streams[stream]
                    self.irc.leave_stream(stream)
                except Exception, e:
                    pp(e)
        elif src == 'twitter':
            if stream in self.twitter_streams:
                try:
                    self.twitter_streams[stream].kill = True
                    del self.twitter_streams[stream]
                    self.twtr.leave_stream(stream)
                except Exception, e:
                    pp(e)

    #featured control
    def get_twitter_api(self):
        try:
            trends = self.twtr.api.trends_place(23424977)
            output = [{'title':x['name'],'stream':[self.pattern.sub('',x['name']).lower()],'description':'','count':x['tweet_volume']} for x in trends[0]['trends'] if x['tweet_volume']!=None]
            sorted_output = sorted(output, key=lambda k: k['count'], reverse=True) 
            sorted_output = sorted_output[0:self.config['twitter_num_featured']]

            streams_to_add = [x['stream'][0] for x in sorted_output]
            streams_to_remove = []

            self.twitter_featured_buffer += streams_to_add

            while len(self.twitter_featured_buffer)>self.config['twitter_featured_buffer_maxlen']:
                old_stream = self.twitter_featured_buffer.pop(0)
                if (old_stream not in self.twitter_featured_buffer) and (old_stream in self.twitter_streams):
                    try:
                        self.twitter_streams[old_stream].kill = True
                        del self.twitter_streams[old_stream]
                    except Exception, e:
                        pp(e)
                    streams_to_remove.append(old_stream)

            self.twtr.batch_streams(streams_to_add, streams_to_remove)

            for featured_stream in streams_to_add:
                self.create_stream(featured_stream, 'twitter')

            self.twitter_api_featured = sorted_output

        except Exception, e:
            pp('Get Twitter API featured failed.')
            pp(e)

    def get_twitter_manual(self):
        try:
            featured_result = self.service.spreadsheets().values().get(spreadsheetId=self.config['spreadsheetID'], range=self.config['featured_live_range']).execute()
            featured_values = featured_result.get('values', [])
            featured_live_bool = int(featured_values[0][0])

            if featured_live_bool == 1:
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

                    self.twtr.batch_streams(addition_manual_streams, current_manual_streams)

                    for featured_stream in addition_manual_streams:
                        self.create_stream(featured_stream, 'twitter')

                    self.twitter_manual_featured = manual_featured

            schedule_result = self.service.spreadsheets().values().get(spreadsheetId=self.config['spreadsheetID'], range=self.config['schedule_live_range']).execute()
            schedule_values = schedule_result.get('values', [])
            schedule_live_bool = int(schedule_values[0][0])

            if schedule_live_bool == 1:
                result = self.service.spreadsheets().values().get(spreadsheetId=self.config['spreadsheetID'], range=self.config['schedule_data_range']).execute()
                values = result.get('values', [])

                schedule = []
                for row in values:
                    schedule.append({'eventname':row[0], 'source':row[1], 'stream':row[2], 'starttime':datetime.datetime.strptime(row[3]+" "+ row[4],"%m/%d/%y %I:%M:%S %p"), 'endtime':datetime.datetime.strptime(row[3]+" "+ row[5],"%m/%d/%y %I:%M:%S %p")})

                if schedule != self.schedule:
                    self.schedule = schedule
                    pp(self.schedule)

        except Exception, e:
            pp('Get Twitter manual featured failed.')
            pp(e)

    def get_twitch_api(self):
        headers = {'Accept':'application/vnd.twitchtv.v3+json', 'Client-ID':self.config['twitch_client_id']}
        try:
            r = self.sess.get('https://api.twitch.tv/kraken/streams', headers = headers)
            output = [{'title':x['channel']['name'], 'stream':[x['channel']['name']], 'image': x['preview']['medium'], 'description': x['channel']['status'], 'game': x['game'], 'count': x['viewers']} for x in (json.loads(r.content))['streams']]
            sorted_output = sorted(output, key=lambda k: k['count'], reverse=True) 
            self.twitch_api_featured = sorted_output[0:self.config['twitch_num_featured']]
        except Exception, e:
            pp('Get Twitch featured failed.')
            pp(e)

    def refresh_featured(self):
        self.refresh_loop = True
        while self.refresh_loop:
            self.get_twitch_api()
            self.get_twitter_api()
            self.get_twitter_manual()

            time.sleep(1200)

    # logging control
    def log_monitor(self):
        self.log_monitor_loop = True

        while self.log_monitor_loop:
            for scheduled_stream in self.schedule:
                try:
                    if (datetime.datetime.now() > scheduled_stream['starttime']) and (datetime.datetime.now() < scheduled_stream['endtime']):
                        if (scheduled_stream['source'] == 'twitch') and (scheduled_stream['stream'] in self.twitch_streams):
                            if self.twitch_streams[scheduled_stream['stream']].log_file is None:
                                self.twitch_streams[scheduled_stream['stream']].log_start_time = scheduled_stream['starttime']
                                self.twitch_streams[scheduled_stream['stream']].log_file = open(self.config['twitch_log_path']+scheduled_stream['stream']+scheduled_stream['starttime'].strftime("%y%m%d_%H%M"), 'w')
                        elif (scheduled_stream['source'] == 'twitter') and (scheduled_stream['stream'] in self.twitter_streams):
                            if self.twitter_streams[scheduled_stream['stream']].log_file is None:
                                self.twitter_streams[scheduled_stream['stream']].log_start_time = scheduled_stream['starttime']
                                self.twitter_streams[scheduled_stream['stream']].log_file = open(self.config['twitter_log_path']+scheduled_stream['stream']+scheduled_stream['starttime'].strftime("%y%m%d_%H%M"), 'w')
                    else:
                        if (scheduled_stream['source'] == 'twitch') and (scheduled_stream['stream'] in self.twitch_streams):
                            if self.twitch_streams[scheduled_stream['stream']].log_file is not None:
                                self.twitch_streams[scheduled_stream['stream']].log_file.close()
                                self.twitch_streams[scheduled_stream['stream']].log_file = None
                                self.twitch_streams[scheduled_stream['stream']].log_start_time = None
                        elif (scheduled_stream['source'] == 'twitter') and (scheduled_stream['stream'] in self.twitter_streams):
                            if self.twitter_streams[scheduled_stream['stream']].log_file is not None:
                                self.twitter_streams[scheduled_stream['stream']].log_file.close()
                                self.twitter_streams[scheduled_stream['stream']].log_file = None
                                self.twitter_streams[scheduled_stream['stream']].log_start_time = None
                except Exception, e:
                    pp(e)

            time.sleep(30)

    # Dataserver connections
    def send_subjs(self):
        self.send_subjs_loop = True
        while self.send_subjs_loop:
            if len(self.twitter_streams.keys()) > 0:
                for stream_key in self.twitter_streams.keys():
                    try:
                        pickled_data = pickle.dumps(('twitter', stream_key, self.twitter_streams[stream_key].get_subjs()))
                        self.subj_sock.send(pickled_data)
                    except Exception, e:
                        pp(e)

            if len(self.twitch_streams.keys()) > 0:
                for stream_key in self.twitch_streams.keys():
                    try:
                        pickled_data = pickle.dumps(('twitch', stream_key, self.twitch_streams[stream_key].get_subjs()))
                        self.subj_sock.send(pickled_data)
                    except Exception, e:
                        pp(e)

            time.sleep(60)

    def recv_clusters(self):
        self.recv_clusters_loop = True
        while self.recv_clusters_loop:
            data = self.cluster_sock.recv()
            src, stream, clusters = pickle.loads(data)
            try:
                if src == 'twitch':
                    self.twitch_streams[stream].set_clusters(clusters)
                elif src == 'twitter':
                    self.twitter_streams[stream].set_clusters(clusters)
            except Exception, e:
                pp(e)

    # Twitch Helpers
    def reset_subjs_twitch(self):
        self.reset_subjs_twitch_loop = True
        while self.reset_subjs_twitch_loop:
            if len(self.twitch_streams.keys()) > 0:
                for stream_key in self.twitch_streams.keys():
                    try:
                        self.twitch_streams[stream_key].reset_subjs()
                    except Exception, e:
                        pp(e)

            time.sleep(600)

    def filter_trending_twitch(self):
        self.filter_trending_twitch_loop = True
        while self.filter_trending_twitch_loop:
            if len(self.twitch_streams.keys()) > 0:
                for stream_key in self.twitch_streams.keys():
                    try:
                        self.twitch_streams[stream_key].filter_trending()
                    except Exception, e:
                        pp(e)
                    
            time.sleep(0.8)

    def render_twitch(self):
        self.render_twitch_loop = True
        while self.render_twitch_loop:
            if len(self.twitch_streams.keys()) > 0:
                for stream_key in self.twitch_streams.keys():
                    try:
                        self.twitch_streams[stream_key].render_trending()
                    except Exception, e:
                        pp(e)

            time.sleep(0.3)

    # Twitter Helpers
    def reset_subjs_twitter(self):
        self.reset_subjs_twitter_loop = True
        while self.reset_subjs_twitter_loop:
            if len(self.twitter_streams.keys()) > 0:
                for stream_key in self.twitter_streams.keys():
                    try:
                        self.twitter_streams[stream_key].reset_subjs()
                    except Exception, e:
                        pp(e)

            if len(self.twitch_streams.keys()) > 0:
                for stream_key in self.twitch_streams.keys():
                    try:
                        self.twitch_streams[stream_key].reset_subjs()
                    except Exception, e:
                        pp(e)

            time.sleep(600)

    def filter_content_twitter(self):
        self.filter_content_twitter_loop = True
        while self.filter_content_twitter_loop:
            if len(self.twitter_streams.keys()) > 0:
                for stream_key in self.twitter_streams.keys():
                    try:
                        self.twitter_streams[stream_key].filter_content()
                    except Exception, e:
                        pp(e)

            time.sleep(15)

    def filter_trending_twitter(self):
        self.filter_trending_twitter_loop = True
        while self.filter_trending_twitter_loop:
            if len(self.twitter_streams.keys()) > 0:
                for stream_key in self.twitter_streams.keys():
                    try:
                        self.twitter_streams[stream_key].filter_trending()
                    except Exception, e:
                        pp(e)

            time.sleep(0.8)

    def render_twitter(self):
        self.render_twitter_loop = True
        while self.render_twitter_loop:
            if len(self.twitter_streams.keys()) > 0:
                for stream_key in self.twitter_streams.keys():
                    try:
                        self.twitter_streams[stream_key].render_trending()
                    except Exception, e:
                        pp(e)
                        
            time.sleep(0.7)

    # Monitors
    def garbage_cleanup(self):
        self.gc_loop = True
        while self.gc_loop:
            gc.collect()

            time.sleep(300)

    def monitor_twitter(self):
        self.monitor_loop = True

        while self.monitor_loop:
            curr_dict = {}

            for stream in self.twitter_streams.values():
                try:
                    curr_dict.update(stream.get_trending())
                except Exception, e:
                    pp(e)

            curr_hash = hash(frozenset(curr_dict))
            if curr_hash == self.twitter_hash:
                pp('Monitor twitter triggered - refreshing!')
                self.twtr.refresh_streams()
            else:
                self.twitter_hash = curr_hash

            time.sleep(15)
