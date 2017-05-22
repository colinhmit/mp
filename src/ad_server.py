import threading
import requests
import json

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

from utils.functions_general import *

class AdServer():
    def __init__(self, config):
        pp('Initializing Ad Server...')

        self.ads = {}
        self.ads['demo'] = {}

        self.init_sockets()
        self.init_threads()

    def init_sockets(self):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(self.config['google_sheets']['sheets_key'], self.config['google_sheets']['scopes'])
        self.service = build('sheets', 'v4', credentials=self.credentials)

        context = zmq.Context()
        self.http_socket = context.socket(zmq.PUSH)
        self.http_socket.connect('tcp://'+self.config['zmq_http_host']+':'+str(self.config['zmq_http_port']))

    def init_threads(self):
        threading.Thread(target = self.refresh_ads, args=(self.config['timeout'],)).start()

    # Helper threads
    def refresh_ads(self, timeout):
        self.refresh_loop = True
        while self.refresh_loop:
            self.get_demo_ads()
            self.send_ads()
            time.sleep(timeout)

    def send_ads(self):
        try:
            data = {
                'type': 'ad',
                'data': self.ads
            }
            pickled_data = pickle.dumps(data)
            self.http_socket.send(pickled_data)
        except Exception, e:
            pp(e)

    def get_demo_ads(self):
        try:
            live_data = self.service.spreadsheets().values().get(spreadsheetId=self.config['google_sheets']['spreadsheetID'], range=self.config['google_sheets']['ad_live_range']).execute()
            live_values = live_data.get('values', [])

            if int(live_values[0][0]) == 1:
                data = self.service.spreadsheets().values().get(spreadsheetId=self.config['google_sheets']['spreadsheetID'], range=self.config['google_sheets']['ad_data_range']).execute()
                values = data.get('values', [])

                ads = {}
                for row in values:
                    ads[row[2]] = {'sponsor':row[0], 'ad_id': row[1], 'media_url':[row[3]], 'score': row[4]}
                
                self.ads['demo'] = ads
                pp(ads)
        except Exception, e:
            pp('Get Ads failed.')
            pp(e)