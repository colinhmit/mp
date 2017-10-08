import multiprocessing

from src.utils._functions_general import *


# Input View Base Framework
class ViewBase:
    def __init__(self, config, streams):
        self.config = config
        self.streams = streams
        self.conn = None

        pp(self.config['src'] + ' view: Initialized.')

    def refresh_streams(self):
        pp(self.config['src'] + ' view: Refreshing streams...')
        pp(self.streams)
        if self.conn.is_alive():
            self.conn.terminate()
        self.conn = multiprocessing.Process(target=self.view_connection)
        self.conn.start()
