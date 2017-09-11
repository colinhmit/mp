import multiprocessing

from _functions_general import *


# Input Base Framework
class InputBase:
    def __init__(self, config):
        self.config = config
        self.streams = []
        self.stream_conn = None

        pp(self.config['src'] + ': Initialized.')

    def refresh_streams(self):
        pp(self.config['src'] + ': Refreshing streams...')
        if self.stream_conn.is_alive():
            self.stream_conn.terminate()
        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams) > 0:
            self.stream_conn.start()

    def reset_streams(self):
        pp(self.config['src'] + ': Resetting streams...')
        self.streams = []
        if self.stream_conn.is_alive():
            self.stream_conn.terminate()
        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams) > 0:
            self.stream_conn.start()

    def join_stream(self, stream):
        if stream not in self.streams:
            pp(self.config['src'] + ': Joining stream %s.' % stream)
            if self.stream_conn.is_alive():
                self.stream_conn.terminate()
            self.streams.append(stream)
            self.stream_conn = multiprocessing.Process(target=self.stream_connection)
            self.stream_conn.start()

    def leave_stream(self, stream):
        if stream in self.streams:
            pp(self.config['src'] + ': Leaving stream %s.' % stream)
            self.streams.remove(stream)
            if self.stream_conn.is_alive():
                self.stream_conn.terminate()
            self.stream_conn = multiprocessing.Process(target=self.stream_connection)
            if len(self.streams) > 0:
                self.stream_conn.start()
            else:
                pp(self.config['src'] + ': No streams to stream from...')

    def batch_streams(self, streams_to_add, streams_to_remove):
        if self.stream_conn.is_alive():
            self.stream_conn.terminate()
        for stream in streams_to_remove:
            if stream in self.streams:
                self.streams.remove(stream)
        for stream in streams_to_add:
            if stream not in self.streams:
                self.streams.append(stream)
        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams) > 0:
            self.stream_conn.start()
