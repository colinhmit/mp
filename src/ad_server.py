import threading
import requests
import json

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

from utils.functions_general import *

class AdServer():
    def __init__(self, config):
        pp('Initializing Native Stream Manager...')

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

                curated = []
                for row in values:
                    curated.append({'title':row[0], 'stream':row[1].split(","), 'enrich':{'twitter':row[2].split(","),'reddit':row[3].split(",")}, 'image':row[5], 'description':row[4], 'count':row[6]})

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
                                self.send_delete([old_stream])
                            except Exception, e:
                                pp(e)

                    for featured_stream in addition_streams:
                        self.add_stream(featured_stream)

                    self.featured = curated
        except Exception, e:
            pp('Get Native manual featured failed.')
            pp(e)