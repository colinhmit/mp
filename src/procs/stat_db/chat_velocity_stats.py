import datetime
import psycopg2
import multiprocessing

# import utils
from src.utils._functions_general import *

class ChatVelocityStats:
    def __init__(self, config):
        self.config = config

        self.velocity_monitor = multiprocessing.Process(target=self.velocity)
        self.velocity_monitor.start()

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

    def velocity(self):
        self.init_db()
        self.vel_time = datetime.datetime.now()

        num_set = False
        while not num_set:
            try:
                self.cur.execute("SELECT max(num) FROM input_chat_stats;")
                max_num = self.cur.fetchall()
                if max_num[0][0]:
                    self.num = max_num[0][0] + 1
                else:
                    self.num = 0
                num_set = True
            except Exception, e:
                pp('error setting num velocity', 'error')

        velocity_monitor = True
        while velocity_monitor:
            self.vel_time = datetime.datetime.now()
            self.cur.execute("SELECT s.src as src, s.stream as stream, s.num_comments as num_comments, s.num_commenters as num_commenters, t.tot_comments as tot_comments, t.tot_commenters as tot_commenters from (SELECT src, stream, COUNT (*) as num_comments, COUNT (DISTINCT username) as num_commenters FROM input_chat WHERE time BETWEEN %s and %s GROUP BY src, stream) as s INNER JOIN (SELECT src, stream, COUNT (*) as tot_comments, COUNT (DISTINCT username) as tot_commenters FROM input_chat GROUP BY src, stream) as t ON s.src=t.src AND s.stream=t.stream;", (self.vel_time - datetime.timedelta(seconds=self.config['lookback']), self.vel_time))
            data = self.cur.fetchall()
            if len(data) > 0:
                args_str = ','.join(self.cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s)", (self.vel_time.replace(microsecond=0).isoformat(), x[0], x[1], self.num, x[2], x[3], x[4], x[5])) for x in data)
                self.cur.execute("INSERT INTO input_chat_stats (time, src, stream, num, num_comments, num_commenters, tot_comments, tot_commenters) VALUES " + args_str)
                self.con.commit()
                self.num += 1
                time.sleep(max(0,self.config['interval']-(datetime.datetime.now()-self.vel_time).total_seconds()))