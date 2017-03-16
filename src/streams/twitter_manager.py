# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""
import threading
import multiprocessing

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

from utils.functions_general import *
from twitter_stream import TwitterStream
from utils.strm_mgr import strm_mgr

class TwitterManager(strm_mgr):
    def __init__(self, config, twtr, init_streams):
        pp('Initializing Twitter Stream Manager...')
        strm_mgr.__init__(self, config, twtr)

        self.curated = []
        self.featured_buffer = []

        for stream in init_streams:
            self.add_stream(stream)

        self.init_featured()
        self.init_threads()

    def init_featured(self):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(self.config['google_sheets']['sheets_key'], self.config['google_sheets']['scopes'])
        self.service = build('sheets', 'v4', credentials=self.credentials)

    def init_threads(self):
        threading.Thread(target = self.refresh_featured, args=(self.config['twitter_featured'],)).start()
        threading.Thread(target = self.send_featured, args=(self.config['twitter_featured'],)).start()

    def add_stream(self, stream):
        try:
            if stream not in self.streams:
                self.streams[stream] = multiprocessing.Process(target=TwitterStream, args=(self.config['twitter_config'], stream)) 
                self.src.join_stream(stream)
                self.streams[stream].start()
        except Exception, e:
            pp(e)
        
    def get_featured(self):
        self.get_curated()
        self.get_featured_api()
        
    def get_featured_api(self):
        try:
            trends = self.src.api.trends_place(23424977)
            output = [{'title':x['name'],'stream':[self.pattern.sub('',x['name']).lower()],'description':'','count':x['tweet_volume'], 'image':''} for x in trends[0]['trends'] if x['tweet_volume']!=None]
            sorted_output = sorted(output, key=lambda k: k['count'], reverse=True) 
            sorted_output = sorted_output[0:self.config['twitter_featured']['num_featured']]

            streams_to_add = [x['stream'][0] for x in sorted_output]
            streams_to_remove = []

            self.featured_buffer += streams_to_add

            while len(self.featured_buffer)>self.config['twitter_featured']['featured_buffer_maxlen']:
                old_stream = self.featured_buffer.pop(0)
                if (old_stream not in self.featured_buffer) and (old_stream in self.streams):
                    try:
                        self.streams[old_stream].terminate()
                        del self.streams[old_stream]
                    except Exception, e:
                        pp(e)
                    streams_to_remove.append(old_stream)

            self.src.batch_streams(streams_to_add, streams_to_remove)

            for featured_stream in streams_to_add:
                self.add_stream(featured_stream)

            self.featured = self.curated + sorted_output

        except Exception, e:
            pp('Get Twitter API featured failed.')
            pp(e)

    def get_curated(self):
        try:
            live_data = self.service.spreadsheets().values().get(spreadsheetId=self.config['google_sheets']['spreadsheetID'], range=self.config['google_sheets']['featured_live_range']).execute()
            live_values = live_data.get('values', [])

            if int(live_values[0][0]) == 1:
                data = self.service.spreadsheets().values().get(spreadsheetId=self.config['google_sheets']['spreadsheetID'], range=self.config['google_sheets']['featured_data_range']).execute()
                values = data.get('values', [])

                curated = []
                for row in values:
                    curated.append({'title':row[0], 'stream':row[1].split(","), 'image':row[3], 'description':row[2], 'count':row[4]})

                if curated != self.curated:
                    current_streams = [x['stream'] for x in self.curated]
                    current_streams = [val for sublist in current_streams for val in sublist]

                    addition_streams = [x['stream'] for x in curated]
                    addition_streams = [val for sublist in addition_streams for val in sublist]

                    for old_stream in current_streams:
                        if (old_stream not in addition_streams) and (old_stream in self.streams):
                            try:
                                self.streams[old_stream].terminate()
                                del self.streams[old_stream]
                            except Exception, e:
                                pp(e)

                    self.src.batch_streams(addition_streams, current_streams)

                    for featured_stream in addition_streams:
                        self.add_stream(featured_stream)

                    self.curated = curated
        except Exception, e:
            pp('Get Twitter manual featured failed.')
            pp(e)