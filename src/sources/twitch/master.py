from src.utils._functions_general import *
from src.sources.twitch.chat import Chat
from src.sources.twitch.view import View


class Master:
    def __init__(self, config, streams):
        self.config = config
        self.streams = streams
        
        self.chat = Chat(self.config['chat_conn_config'], self.streams)
        self.view = View(self.config['view_conn_config'], self.streams)

    def refresh(self):
        self.chat.refresh_streams()
        self.view.refresh_streams()