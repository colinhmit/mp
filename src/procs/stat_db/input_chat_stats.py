import datetime
import psycopg2

# import utils
from src.utils._functions_general import *

class InputChatStats:
    def __init__(self, config):
        self.config = config
        self.time = datetime.datetime.now()

        self.init_db()

        self.num = 0
        self.monitor()

    def init_db(self):
        self.con = psycopg2.connect(dbname=self.config['db_str'],
                                    host=self.config['host_str'],
                                    port=self.config['port_str'],
                                    user=self.config['user_str'],
                                    password=self.config['pw_str'])
        self.cur = self.con.cursor()

    def monitor(self):
        monitoring = True
        while monitoring:
            self.time = datetime.datetime.now()
            self.cur.execute("SELECT s.src as src, s.stream as stream, s.num_comments as num_comments, s.num_commenters as num_commenters, t.tot_comments as tot_comments, t.tot_commenters as tot_commenters from (SELECT src, stream, COUNT (*) as num_comments, COUNT (DISTINCT username) as num_commenters FROM input_chat WHERE time BETWEEN %s and %s GROUP BY src, stream) as s INNER JOIN (SELECT src, stream, COUNT (*) as tot_comments, COUNT (DISTINCT username) as tot_commenters FROM input_chat GROUP BY src, stream) as t ON s.src=t.src AND s.stream=t.stream;", (self.time - datetime.timedelta(seconds=self.config['lookback']), self.time))
            data = self.cur.fetchall()
            if len(data) > 0:
                args_str = ','.join(self.cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s)", (self.time.replace(microsecond=0).isoformat(), x[0], x[1], self.num, x[2], x[3], x[4], x[5])) for x in data)
                self.cur.execute("INSERT INTO input_chat_stats (time, src, stream, num, num_comments, num_commenters, tot_comments, tot_commenters) VALUES " + args_str)
                self.con.commit()
                self.num += 1
                time.sleep(self.config['interval']-(datetime.datetime.now()-self.time).total_seconds())