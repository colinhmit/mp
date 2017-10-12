import threading
import datetime
import multiprocessing

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
from pytz import timezone

from src.streams.stream import Stream
from src.utils._functions_general import *

class SchedulerMaster:
    def __init__(self, config, srcs, streams):
        pp('Initializing Interface...')
        self.config = config
        self.srcs = srcs
        self.streams = streams

        self.schedule = []
        self.init_sockets()
        self.init_threads()

    def init_sockets(self):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(self.config['sheets_key'], self.config['scopes'])
        self.service = build('sheets', 'v4', credentials=self.credentials)

    def init_threads(self):
        threading.Thread(target = self.get_schedule).start()
        threading.Thread(target = self.set_streams).start()

    def get_schedule(self):
        get_schedule_loop = True

        while get_schedule_loop:
            try:
                live_data = self.service.spreadsheets().values().get(spreadsheetId=self.config['spreadsheetID'], range=self.config['live_range']).execute()
                live_values = live_data.get('values', [])
                if live_values[0][0] == 'TRUE':
                    data = self.service.spreadsheets().values().get(spreadsheetId=self.config['spreadsheetID'], range=self.config['data_range']).execute()
                    values = data.get('values', [])
                    schedule = []
                    for row in values:
                        try:
                            event = {'src': row[0], 'stream':row[1], 'date': row[2], 'start_time':row[3], 'end_time':row[4], 'chat_con': row[5], 'view_con': row[6]}
                            schedule.append(event)
                        except Exception, e:
                            pp('row length wrong', 'error')
                            pp(e, 'error')
                            
                    self.schedule = schedule
            except Exception, e:
                pp('Get schedule failed.')
                pp(e)
            time.sleep(self.config['get_schedule_refresh'])

    def set_streams(self):
        set_streams_loop = True

        tz = timezone(self.config['timezone'])
        while set_streams_loop:
            schedule = list(self.schedule)

            for event in schedule:
                try:
                    start_time = datetime.datetime.strptime(event['date']+" "+event['start_time'],"%m/%d/%y %I:%M:%S %p")
                    end_time = datetime.datetime.strptime(event['date']+" "+event['end_time'],"%m/%d/%y %I:%M:%S %p")
                    curr_time = datetime.datetime.now(tz)
                    if (curr_time > tz.localize(start_time)) & (curr_time < tz.localize(end_time)):
                        if event['stream'] not in self.streams[event['src']]:
                            pp('Scheduler: Adding stream')
                            pp(event)
                            self.streams[event['src']][event['stream']] = {
                                'chat_con': event['chat_con'],
                                'view_con': event['view_con'],
                                'stream':   multiprocessing.Process(target=Stream,
                                                                    args=(self.config['stream_config'],
                                                                          self.config['src_configs'][event['src']],
                                                                          event['stream']))
                            }
                            self.srcs[event['src']].refresh()
                            self.streams[event['src']][event['stream']]['stream'].start()
                    else:
                        if event['stream'] in self.streams[event['src']]:
                            self.streams[event['src']][event['stream']]['stream'].terminate()
                            del self.streams[event['src']][event['stream']]
                            self.srcs[event['src']].refresh()
                except Exception, e:
                    pp('Set stream failed!', 'error')
                    pp(event, 'error')
                    pp(e, 'error')

            time.sleep(self.config['set_streams_refresh'])
                

