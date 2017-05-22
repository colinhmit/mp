import threading
import multiprocessing

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

from utils.functions_general import *
from utils.twitter_stream import TwitterStream
from strm_mgr import strm_mgr

class TwitterManager(strm_mgr):
    def __init__(self, config, twtr, init_streams):
        pp('Initializing Twitter Stream Manager...')
        strm_mgr.__init__(self, config, config['twitter_config']['self'], twtr)

        self.curated_enrich = []
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

    def add_stream(self, stream):
        try:
            if stream not in self.streams:
                self.streams[stream] = multiprocessing.Process(target=TwitterStream, args=(self.config['twitter_config'], stream)) 
                self.inpt.join_stream(stream)
                self.streams[stream].start()
        except Exception, e:
            pp(e)
        
    def get_featured(self):
        self.get_curated()
        self.get_featured_api()
        
    def get_featured_api(self):
        try:
            trends = self.inpt.api.trends_place(23424977)
            output = [{'title':x['name'],'stream':[self.pattern.sub('',x['name']).lower()],'enrich':{'twitter':[self.pattern.sub('',x['name']).lower()]},'description':'','count':x['tweet_volume'], 'image':''} for x in trends[0]['trends'] if x['tweet_volume']!=None]
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

            self.inpt.batch_streams(streams_to_add, streams_to_remove)
            self.send_delete(streams_to_remove)

            for featured_stream in streams_to_add:
                self.add_stream(featured_stream)

            self.featured = sorted_output
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

                curated_enrich = []
                for row in values:
                    curated_enrich.extend(row[2].split(","))

                if curated_enrich != self.curated_enrich:
                    for old_stream in self.curated_enrich:
                        if (old_stream not in curated_enrich) and (old_stream in self.streams):
                            try:
                                self.streams[old_stream].terminate()
                                del self.streams[old_stream]
                                self.send_delete([old_stream])
                            except Exception, e:
                                pp(e)

                    self.inpt.batch_streams(curated_enrich, self.curated_enrich)

                    for featured_stream in curated_enrich:
                        self.add_stream(featured_stream)

                    self.curated_enrich = curated_enrich
        except Exception, e:
            pp('Get Twitter manual featured failed.')
            pp(e)