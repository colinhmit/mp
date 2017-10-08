import multiprocessing
import importlib

#import utils
from src.utils._functions_general import *
from src.streams.stream import Stream
from src.procs.proc_server import ProcServer

from src.config.server_config import server_config


class Server:
    def __init__(self, config):
        self.config = config

        self.init_streams()
        self.init_srcs()
        self.init_procs()

    def init_streams(self):
        self.streams = {}
        for src in self.config['src_configs'].keys():
            if self.config['src_on'][src]:
                self.streams[src] = {}

    def init_srcs(self):
        self.srcs = {}
        for src in self.config['src_modules'].keys():
            if self.config['src_on'][src]:
                module = importlib.import_module(self.config['src_modules'][src])
                Master = getattr(module, 'Master')
                self.srcs[src] = Master(self.config['src_configs'][src], self.streams[src])

    def init_procs(self):
        self.proc = ProcServer(self.config['proc_config'])

    def add_stream(self, src, stream, stream_config):
        try:
            if stream not in self.streams[src]:
                self.streams[src][stream] = {
                    'chat_con': stream_config['chat_con'],
                    'view_con': stream_config['view_con'],
                    'stream':   multiprocessing.Process(target=Stream,
                                                        args=(self.config['stream_config'],
                                                              self.config['src_configs'][src],
                                                              stream))
                }
                self.srcs[src].refresh()
                self.streams[src][stream]['stream'].start()
        except Exception, e:
            pp(src + ":" + stream + ': failed adding stream', 'error')
            pp(e, 'error')

    def delete_stream(self, src, stream):
        try:
            if stream in self.streams[src]:
                self.streams[src][stream]['stream'].terminate()
                del self.streams[src][stream]
                self.srcs[src].chat.refresh_streams()
        except Exception, e:
            pp(src + ":" + stream + ': failed deleting stream', 'error')
            pp(e, 'error')

if __name__ == '__main__':
    #init
    server = Server(server_config)

    # skt_replay = {'logfile': 'skt_rox_g5', 'stream': 'skt_rox', 'timestart': 0, 'src': 'internal'}
    # server.srcs['internal'].start_replay(skt_replay)
    # server.add_stream('internal', 'skt_rox', {'chat_con': False})

    #server.srcs['reddit'].start_replay('58pj7j', 'skt_rox', 10, 600)
    #server.add_stream('reddit', 'skt_rox', {'chat_con': False})

    server.add_stream('twitch', 'riotgames', {'chat_con': True, 'view_con': True})
    #server.add_stream('twitch', 'riotgames')
    #server.add_stream('twitter', 'trump')
    # server.add_stream('reddit', 'soccer')

    # server.add_stream('twitter', 'nfl')
    # server.add_stream('reddit', 'nfl')