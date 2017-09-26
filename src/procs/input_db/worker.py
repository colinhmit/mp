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

            if len(data) == 9:
                self.write_input_chat(data)
            elif len(data) == 4:
                self.write_stream_chat(data)

    def write_input_chat(self, data):
        pp('writing.')
        self.cur.execute("INSERT INTO input_chat (time, src, stream, username, message, uuid, src_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", (datetime.datetime.now().isoformat(),data['src'],data['stream'],data['username'],data['message'],data['id'],data['src_id']))
        self.con.commit()

    def write_stream_chat(self, data):
        pp('writing.')
        self.cur.execute("INSERT INTO input_chat (time, src, stream, username, message, uuid, src_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", (datetime.datetime.now().isoformat(),data['src'],data['stream'],data['username'],data['message'],data['id'],data['src_id']))
        self.con.commit()