import psycopg2
import multiprocessing
import datetime

# import utils
from src.utils._functions_general import *
from src.procs.cache_db.worker import Worker
from src.procs.cache_db.distributor import Distributor


class CacheDBMaster:
    def __init__(self, config):
        pp('Initializing Cache DB Master...')
        self.config = config

        self.proc = multiprocessing.Process(target=self.run)
        self.proc.start()

    def run(self):
        self.init_db()
        self.init_cache()

        self.workers = []
        self.start_workers()

        while True:
            pass

    def init_db(self):
        self.con = psycopg2.connect(dbname=self.config['worker_config']['db_str'],
                                    host=self.config['worker_config']['host_str'],
                                    port=self.config['worker_config']['port_str'],
                                    user=self.config['worker_config']['user_str'],
                                    password=self.config['worker_config']['pw_str'])
        self.cur = self.con.cursor()

    def init_cache(self):
        self.cache = {}

        for init in self.config['init_cache']:
            if init['table'] not in self.cache:
                self.cache[init['table']] = {}

            if init['src'] not in self.cache[init['table']]:
                self.cache[init['table']][init['src']] = {}

            if init['stream'] not in self.cache[init['table']][init['src']]:
                self.cache[init['table']][init['src']][init['stream']] = {}

            for num in range(init['start_num'], init['end_num'] + 1):
                pp('Getting: ' + init['table']+':'+init['src']+':'+init['stream']+':'+str(num))
                self.cache[init['table']][init['src']][init['stream']][num] = []

                col_str = ""
                for col in init['columns']:
                    col_str += " " + col + ","
                param_str = "src='" + init['src'] + "' AND " + "stream='" + init['stream'] + "' AND " + "num=" + str(num)
                execute_str = "SELECT " + col_str[:-1] + " FROM " + init['table'] + " WHERE " + param_str + ";"
                self.cur.execute(execute_str)
                fetchs = self.cur.fetchall()

                for fetch in fetchs:
                    result = {}
                    if len(fetch) != len(init['columns']):
                        pp('Result did not match length of colums!', 'error')
                        pp(result, 'error')
                        pp(init, 'error')
                    else:
                        for i in range(0, len(fetch)):
                            if isinstance(fetch[i], datetime.date):
                                result[init['columns'][i]] = fetch[i].isoformat()
                            else:
                                result[init['columns'][i]] = fetch[i]
                        self.cache[init['table']][init['src']][init['stream']][num].append(result)
        self.cur.close()
        self.con.close()

    def start_workers(self):
        for _ in xrange(self.config['num_workers']):
            self.workers.append(Worker(self.config['worker_config'], self.cache))
