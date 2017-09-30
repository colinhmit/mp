import zmq
import pickle
import multiprocessing

# import utils
from src.utils._functions_general import *
from src.config.socket_config import *

worker_config = {
    # db connect
    'db_str': 'testdb',
    'host_str': 'currentsdb.clocpkfrofip.us-west-2.rds.amazonaws.com',
    'port_str': '5432',
    'user_str': 'currentsdev',
    'pw_str': 'AndrewColinEben!',

    # messaging
    'funnel_host': DB_HOST,
    'funnel_ports': {
        'input_chat':     DB_PORT_INPUT_CHAT,
        'stream_chat':    DB_PORT_STREAM_CHAT
    }
}

class Worker:
    def __init__(self, config):
        self.config = config

        self.context = zmq.Context()
        self.set_sock()
        self.process()

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
                pp('flushing input_chat from: ' + data['src'] + " : " + data['stream'])
            elif data.get('type', '') == 'stream_chat':
                pp('flushing stream_chat from: ' + data['src'] + " : " + data['stream'])



workers = []
for _ in xrange(15):
            workers.append(multiprocessing.Process(target=Worker,
                                                        args=(worker_config,)
                                                       ).start())
