import threading
import multiprocessing

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

from utils.functions_general import *
from utils.reddit_stream import RedditStream
from strm_mgr import strm_mgr

class RedditManager(strm_mgr):
    def __init__(self, config, rddt, init_streams):
        pp('Initializing Reddit Stream Manager...')
        strm_mgr.__init__(self, config, config['reddit_config']['self'], rddt)

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
        pass

    def get_featured(self):
        self.get_curated()
        
    def get_curated(self):
        try:
            live_data = self.service.spreadsheets().values().get(spreadsheetId=self.config['google_sheets']['spreadsheetID'], range=self.config['google_sheets']['featured_live_range']).execute()
            live_values = live_data.get('values', [])

            if int(live_values[0][0]) == 1:
                data = self.service.spreadsheets().values().get(spreadsheetId=self.config['google_sheets']['spreadsheetID'], range=self.config['google_sheets']['featured_data_range']).execute()
                values = data.get('values', [])

                curated_enrich = []
                for row in values:
                    curated_enrich.extend(row[3].split(","))

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

    def add_stream(self, stream):
        try:
            if stream not in self.streams:
                self.streams[stream] = multiprocessing.Process(target=RedditStream, args=(self.config['reddit_config'], stream)) 
                self.inpt.join_stream(stream)
                self.streams[stream].start()
        except Exception, e:
            pp(e)