import zmq
import pickle
import datetime
import psycopg2
import numpy
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

# import utils
from src.utils._functions_general import *


class Worker:
    def __init__(self, config):
        self.config = config

        self.SIA = SIA()
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
            elif data.get('type', '') == 'input_view':
                self.write_input_view(data)
            elif data.get('type', '') == 'stream_trending':
                self.write_stream_trending(data)
            elif data.get('type', '') == 'stream_nlp':
                self.write_stream_nlp(data)

    def write_input_chat(self, data):
        self.cur.execute("INSERT INTO input_chat (time, src, stream, username, message, uuid, src_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", (data['time'],data['src'],data['stream'],data['username'],data['message'],data['id'],data['src_id']))
        self.con.commit()

    def write_input_view(self, data):
        self.cur.execute("INSERT INTO input_view (time, src, stream, num, num_viewers) VALUES (%s, %s, %s, %s, %s)", (data['time'],data['src'],data['stream'],data['num'],data['num_viewers']))
        self.con.commit()

    def write_stream_trending(self, data):
        if len(data['data']) > 0:
            trending = data['data']
            args_str = ','.join(self.cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (data['time'], data['src'], data['stream'], data['num'], trending[k]['username'], trending[k]['score'], k, trending[k]['first_rcv_time'], trending[k]['id'], trending[k]['src_id'])) for k in trending.keys())
            self.cur.execute("INSERT INTO trending (time, src, stream, num, username, score, message, first_rcv_time, uuid, src_id) VALUES " + args_str)
            self.con.commit()

    def write_stream_nlp(self, data):
        if len(data['data']) > 0:
            nlp = data['data']
            result = []
            for subj in nlp:
                dp_scores = {}
                scores = []
                for message in nlp[subj]['messages']:
                    if message in dp_scores:
                        if dp_scores[message] != 0.0:
                            scores.append(dp_scores[message])
                    else:
                        score = self.SIA.polarity_scores(message)['compound']*100.0
                        dp_scores[message] = score
                        if score != 0.0:
                            scores.append(score)

                if len(scores) > 0:
                    result.append((subj, nlp[subj]['score'], numpy.mean(scores)))
                else:
                    result.append((subj, nlp[subj]['score'], 0.0))

            args_str = ','.join(self.cur.mogrify("(%s,%s,%s,%s,%s,%s,%s)", (data['time'], data['src'], data['stream'], data['num'], x[0], x[1], x[2])) for x in result)
            self.cur.execute("INSERT INTO subjects (time, src, stream, num, subject, score, sentiment) VALUES " + args_str)
            self.con.commit()
