import zmq
import json
import datetime
import psycopg2
import threading

# import utils
from src.utils._functions_general import *


class Worker:
    def __init__(self, config, cache):
        self.config = config
        self.cache = cache
        self.context = zmq.Context()
        self.set_sock()
        self.init_db()
        
        self.thread = threading.Thread(target=self.process)
        self.thread.start()

    def init_db(self):
        self.con = psycopg2.connect(dbname=self.config['db_str'],
                                    host=self.config['host_str'],
                                    port=self.config['port_str'],
                                    user=self.config['user_str'],
                                    password=self.config['pw_str'])
        self.cur = self.con.cursor()

    def set_sock(self):        
        self.sock = self.context.socket(zmq.REP)
        self.sock.connect('tcp://' +
                          self.config['worker_host'] +
                          ':' + str(self.config['worker_port']))

    def process(self):
        for data in iter(self.sock.recv, 'STOP'):
            try:
                data = json.loads(data)
                if data.get('type', '') == 'num_req':
                    cache_response = self.get_data_from_cache(data)
                    if len(cache_response) > 0:
                        pp('responding')
                        self.sock.send(json.dumps(cache_response))
            except Exception, e:
                pp(e, 'error')

    def get_data_from_cache(self, data):
        result = []
        for num in range(data['start_num'], data['end_num'] + 1):
            try:
                cache_rows = self.cache[data['table']][data['src']][data['stream']][num]
                for row in cache_rows:
                    out_row = {}
                    for col in data['columns']:
                        out_row[col] = row[col]
                    result.append(out_row)
            except Exception, e:
                pp('failed getting data from cache for num = ' + str(num) + '!', 'error')
                pp(data, 'error')
                pp(e, 'error')
        return result

    def get_data_from_db(self, data):
        pass
        # col_str = ""
        # for col in data['columns']:
        #     col_str += " " + col + ","
        # col_str[:-1]

        # param_str = "src=" + data['src'] + " AND " + "stream=" + data['stream'] + " AND " + "num BETWEEN " + str(data['start_num']) + " and " + str(data['end_num'])

        # execute_str = "SELECT " + col_str[:-1] + " FROM " + data['table'] + " WHERE " + param_str + ";"
        # self.cur.execute(execute_str)
        # 