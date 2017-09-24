import multiprocessing

from src.utils._functions_general import *


# Input Chat Base Framework
class ChatBase:
    def __init__(self, config, streams):
        self.config = config
        self.streams = streams
        self.conn = None

        pp(self.config['src'] + ': Initialized.')

    def refresh_streams(self):
        pp(self.config['src'] + ': Refreshing streams...')
        pp(self.streams)
        if self.conn.is_alive():
            self.conn.terminate()
        self.conn = multiprocessing.Process(target=self.chat_connection)
        self.conn.start()

    # def reset_streams(self):
    #     pp(self.config['src'] + ': Resetting streams...')
    #     self.streams = []
    #     if self.conn.is_alive():
    #         self.conn.terminate()
    #     self.conn = multiprocessing.Process(target=self.chat_connection)
    #     if len(self.streams) > 0:
    #         self.conn.start()

    # def join_stream(self, stream):
    #     if stream not in self.streams:
    #         pp(self.config['src'] + ': Joining stream %s.' % stream)
    #         if self.conn.is_alive():
    #             self.conn.terminate()
    #         self.streams.append(stream)
    #         self.conn = multiprocessing.Process(target=self.chat_connection)
    #         self.conn.start()

    # def leave_stream(self, stream):
    #     if stream in self.streams:
    #         pp(self.config['src'] + ': Leaving stream %s.' % stream)
    #         self.streams.remove(stream)
    #         if self.conn.is_alive():
    #             self.conn.terminate()
    #         self.conn = multiprocessing.Process(target=self.chat_connection)
    #         if len(self.streams) > 0:
    #             self.conn.start()
    #         else:
    #             pp(self.config['src'] + ': No streams to stream from...')

    # def batch_streams(self, streams_to_add, streams_to_remove):
    #     if self.conn.is_alive():
    #         self.conn.terminate()
    #     for stream in streams_to_remove:
    #         if stream in self.streams:
    #             self.streams.remove(stream)
    #     for stream in streams_to_add:
    #         if stream not in self.streams:
    #             self.streams.append(stream)
    #     self.conn = multiprocessing.Process(target=self.chat_connection)
    #     if len(self.streams) > 0:
    #         self.conn.start()
