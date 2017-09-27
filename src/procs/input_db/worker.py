import zmq
import pickle
import datetime
import psycopg2

# import utils
from src.utils._functions_general import *

class Worker:
    def __init__(self, config):
        self.config = config

        self.init_db()

        self.context = zmq.Context()
        self.set_sock()
        self.process()

    def init_db(self):
        self.con = psycopg2.connect(dbname=self.config['db_str'],
                                    host=self.config['host_str'],
                                    port=self.config['port_str'],
                                    user=self.config['user_str'],
                                    password=self.config['pw_str'])
        self.cur = self.con.cursor()

    def set_sock(self):
        self.sock = self.context.socket(zmq.PULL)
        for src in self.config['funnel_ports'].keys():
            self.sock.connect('tcp://' +
                              self.config['funnel_host'] +
                              ':' +
                              str(self.config['funnel_ports'][src]))

    def process(self):
        for data in iter(self.sock.recv, 'STOP'):
            data = pickle.loads(data)

            if data.get('type', '') == 'input_chat':
                self.write_input_chat(data)
            elif data.get('type', '') == 'stream_chat':
                self.write_stream_chat(data)

    def write_input_chat(self, data):
        self.cur.execute("INSERT INTO input_chat (time, src, stream, username, message, uuid, src_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", (data['time'],data['src'],data['stream'],data['username'],data['message'],data['id'],data['src_id']))
        self.con.commit()

    def write_stream_chat(self, data):
        if 'trending' in  data['data'] and len(data['data'].get('trending',{})) > 0:
            trending = data['data']['trending']
            args_str = ','.join(self.cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (data['time'], data['src'], data['stream'], data['num'], trending[k]['username'], trending[k]['score'], k, trending[k]['first_rcv_time'], trending[k]['id'], trending[k]['src_id'])) for k in trending.keys())
            self.cur.execute("INSERT INTO stream_chat (time, src, stream, num, username, score, message, first_rcv_time, uuid, src_id) VALUES " + args_str)
            self.con.commit()