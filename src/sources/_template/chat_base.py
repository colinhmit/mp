import multiprocessing

from src.utils._functions_general import *


# Input Chat Base Framework
class ChatBase:
    def __init__(self, config, streams):
        self.config = config
        self.streams = streams
        self.conn = None

        pp(self.config['src'] + ' chat: Initialized.')

    def refresh_streams(self):
        pp(self.config['src'] + ' chat: Refreshing streams...')
        if self.conn.is_alive():
            self.conn.terminate()
        self.conn = multiprocessing.Process(target=self.chat_connection)
        self.conn.start()