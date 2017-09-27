import datetime
import psycopg2

# import utils
from src.utils._functions_general import *

class InputChatStats:
    def __init__(self, config):
        self.config = config
        self.time = datetime.datetime.now()

        self.init_db()
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
            self.cur.execute("SELECT src, stream, COUNT (*), COUNT (DISTINCT username) FROM input_chat WHERE time BETWEEN %s and %s GROUP BY src, stream;", (self.time - datetime.timedelta(seconds=self.config['interval']), self.time))
            data = self.cur.fetchall()
            if len(data) > 0:
                args_str = ','.join(self.cur.mogrify("(%s,%s,%s,%s,%s)", (self.time.replace(microsecond=0).isoformat(), x[0], x[1], x[2], x[3])) for x in data)
                self.cur.execute("INSERT INTO input_chat_stats (time, src, stream, num_comments, num_commenters) VALUES " + args_str)
                self.con.commit()
                time.sleep(self.config['interval']-(datetime.datetime.now()-self.time).total_seconds())