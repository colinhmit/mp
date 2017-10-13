import json
import socket
import zmq
import requests
import pickle
import multiprocessing
import datetime
import psycopg2

from src.utils._functions_general import *
from src.sources._template.view_base import ViewBase


class View(ViewBase):
    def __init__(self, config, streams):
        ViewBase.__init__(self, config, streams)
        self.config = config

        self.conn = multiprocessing.Process(target=self.view_connection)
        self.conn.start()

    def view_connection(self):
        view_streams = [k for k, v in self.streams.items() if v['view_con']]
        if len(view_streams) > 0:        
            self.context = zmq.Context()
            self.init_db()

            self.set_sock()
            self.set_pipe()

            query = "SELECT max(num) FROM input_view WHERE src='twitch';"
            num_set = False
            while not num_set:
                try:
                    self.cur.execute(query)
                    max_num = self.cur.fetchall()
                    if max_num[0][0]:
                        self.num = max_num[0][0] + 1
                    else:
                        self.num = 0
                    num_set = True
                except Exception, e:
                    pp('error setting num', 'error')
            
            connected = True
            while connected:
                try:
                    headers = {'Client-ID':self.config['client_id']}
                    params = 'user_login='
                    for stream in view_streams:
                        params += stream + ','
                    r = self.sess.get('https://api.twitch.tv/helix/streams?'+params[:-1], headers=headers)
                    data = json.loads(r.content)
                    curr_time = datetime.datetime.now().isoformat(),
                    results = [{
                                'type':     'input_view',
                                'src':      self.config['src'],
                                'time':     curr_time,
                                'num':      self.num,
                                'stream': x['thumbnail_url'][x['thumbnail_url'].find('live_user_')+10:x['thumbnail_url'].find('-{width}')],
                                'num_viewers': x['viewer_count']
                              } for x in data['data']]
                    for result in results:
                        self.pipe.send(pickle.dumps(result))
                    self.num += 1
                except Exception, e:
                    pp('//////TWITCH VIEW CONNECT ERROR!////', 'error')
                    pp(e, 'error')

                time.sleep(self.config['view_refresh'])
    
    def init_db(self):
        db_connect = False

        while not db_connect:
            try:
                self.con = psycopg2.connect(dbname=self.config['db_str'],
                                            host=self.config['host_str'],
                                            port=self.config['port_str'],
                                            user=self.config['user_str'],
                                            password=self.config['pw_str'])
                self.cur = self.con.cursor()
                db_connect = True
            except Exception, e:
                pp(e, 'error')
                time.sleep(self.config['db_connect_timeout'])

        

    def set_sock(self):
        self.sess = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.sess.mount('https://api.twitch.tv', adapter)
        self.sess.trust_env = False

    def set_pipe(self):
        self.context = zmq.Context()
        self.pipe = self.context.socket(zmq.PUB)
        self.pipe.connect('tcp://'+self.config['fwd_host']+':'+str(self.config['fwd_port']))
