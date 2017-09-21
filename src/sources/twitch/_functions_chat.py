import json
import uuid

from src.utils._functions_general import *

# 1. Twitch Parser
# 2. Twitch Check Stream


def parse(data):
    # try: data may be corrupt
    try:
        msg = {
               'src':           'twitch',
               'stream':        re.findall(r'^:.+\![a-zA-Z0-9_]'
                                           r'+@[a-zA-Z0-9_]'
                                           r'+.+ PRIVMSG (.*?) :',
                                           data)[0][1:].lower(),
               'username':      re.findall(r'^:([a-zA-Z0-9_]+)\!',
                                           data)[0],
               'message':       re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)',
                                           data)[0],
               'media_urls':    [],
               'mp4_url':       '',
               'id':            str(uuid.uuid1()),
               'src_id':        ''
              }
        return msg
    except Exception, e:
        pp('parse_twitch failed', 'error')
        pp(e, 'error')
        return {}


def check_stream(stream, data):
    # try: data may be empty etc?
    try:
        if stream == data['stream']:
            return True
        else:
            return False
    except Exception, e:
        pp('check_stream twitch failed', 'error')
        pp(e)
        return False
