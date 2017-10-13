import datetime
import psycopg2
import numpy
import multiprocessing
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA


# import utils
from src.utils._functions_general import *

class ChatSentimentStats:
    def __init__(self, config):
        self.config = config
        self.SIA = SIA()

        self.input_sentiment_monitor = multiprocessing.Process(target=self.input_sentiment)
        self.input_sentiment_monitor.start()

        self.stream_sentiment_monitor = multiprocessing.Process(target=self.stream_sentiment)
        self.stream_sentiment_monitor.start()

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

    def input_sentiment(self):
        self.init_db()
        self.input_time = datetime.datetime.now()

        num_set = False
        while not num_set:
            try:
                self.cur.execute("SELECT max(num) FROM sentiment WHERE type='input';")
                max_num = self.cur.fetchall()
                if max_num[0][0]:
                    self.num = max_num[0][0] + 1
                else:
                    self.num = 0
                num_set = True
            except Exception, e:
                pp('error setting num input sent', 'error')

        input_sentiment_monitor = True
        while input_sentiment_monitor:
            self.input_time = datetime.datetime.now()
            self.cur.execute("SELECT array_agg(message), src, stream FROM input_chat WHERE time BETWEEN %s and %s GROUP BY src, stream;", (self.input_time - datetime.timedelta(seconds=self.config['lookback']), self.input_time))
            datas = self.cur.fetchall()

            if len(datas) > 0:
                result = []
                for data in datas:
                    dp_scores = {}
                    scores = []
                    for text in data[0]:
                        if text in dp_scores:
                            scores.append(dp_scores[text])
                        else:
                            score = self.SIA.polarity_scores(text)['compound']*100.0
                            dp_scores[text] = score
                            scores.append(score)

                    #scores = [self.SIA.polarity_scores(x)['compound'] for x in data[0]]
                    result.append((data[1], data[2], numpy.mean(scores)))

                args_str = ','.join(self.cur.mogrify("(%s,%s,%s,%s,%s,%s)", (self.input_time.replace(microsecond=0).isoformat(), x[0], x[1], 'input', self.num, x[2])) for x in result)
                self.cur.execute("INSERT INTO sentiment (time, src, stream, type, num, sentiment) VALUES " + args_str)
                self.con.commit()
                self.num += 1
                time.sleep(max(0,self.config['interval']-(datetime.datetime.now()-self.input_time).total_seconds()))

    def stream_sentiment(self):
        self.init_db()
        self.stream_time = datetime.datetime.now()

        num_set = False
        while not num_set:
            try:
                self.cur.execute("SELECT max(num) FROM sentiment WHERE type='stream';")
                max_num = self.cur.fetchall()
                if max_num[0][0]:
                    self.num = max_num[0][0] + 1
                else:
                    self.num = 0
                num_set = True
            except Exception, e:
                pp('error setting num stream sent', 'error')

        input_sentiment_monitor = True
        while input_sentiment_monitor:
            self.stream_time = datetime.datetime.now()
            self.cur.execute("SELECT array_agg(message), array_agg(score), src, stream FROM trending WHERE time BETWEEN %s and %s GROUP BY src, stream;", (self.stream_time - datetime.timedelta(seconds=self.config['lookback']), self.stream_time))
            datas = self.cur.fetchall()

            if len(datas) > 0:
                result = []
                for data in datas:
                    dp_scores = {}
                    scores = []
                    for text in data[0]:
                        if text in dp_scores:
                            scores.append(dp_scores[text])
                        else:
                            score = self.SIA.polarity_scores(text)['compound']*100.0
                            dp_scores[text] = score
                            scores.append(score)

                    #scores = [self.SIA.polarity_scores(x)['compound'] for x in data[0]]
                    result.append((data[2], data[3], numpy.dot(scores, data[1])/sum(data[1])))

                args_str = ','.join(self.cur.mogrify("(%s,%s,%s,%s,%s,%s)", (self.stream_time.replace(microsecond=0).isoformat(), x[0], x[1], 'stream', self.num, x[2])) for x in result)
                self.cur.execute("INSERT INTO sentiment (time, src, stream, type, num, sentiment) VALUES " + args_str)
                self.con.commit()
                self.num += 1
                time.sleep(max(0,self.config['interval']-(datetime.datetime.now()-self.stream_time).total_seconds()))