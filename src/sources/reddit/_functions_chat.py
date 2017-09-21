import json
import uuid

from src.utils._functions_general import *

# 1. Reddit Parser
# 2. Reddit Check Stream


def parse(data):
    # try: data may be corrupt
    try:
        data = json.loads(data)
        msg = {
               'src':           'reddit',
               'stream':        data.get('stream', ''),
               'username':      data.get('username', ''),
               'message':       data.get('message', ''),
               'media_urls':    data.get('media_urls', []),
               'mp4_url':       '',
               'id':            str(uuid.uuid1()),
               'src_id':        data.get('src_id', '')
              }
        return msg
    except Exception, e:
        pp('parse_reddit failed', 'error')
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
        pp('check_stream reddit failed', 'error')
        pp(e)
        return False