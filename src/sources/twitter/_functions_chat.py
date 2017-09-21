import json
import uuid

from src.utils._functions_general import *

# 1. Twitter Parser
# 2. Twitter Check Stream


def parse(data):
    # try: data may be corrupt
    try:
        data = json.loads(data)

        if data.get('possibly_sensitive', False):
            return {}

        msg = {
               'src':           'twitter',
               'username':      data['user']['name'],
               'message':       '',
               'media_urls':    [],
               'mp4_url':       '',
               'id':            str(uuid.uuid1()),
               'src_id':        data['id_str']
              }

        if data.get('retweeted_status', {}).get('text', False):
            msg['message'] = data['retweeted_status']['text']
            if data['retweeted_status']['entities'].get('media', False):
                msg['media_urls'] = [data['retweeted_status']['entities']['media'][0]['media_url']]
                if (data.get('extended_entities', {})
                        .get('media', [{}])[0]
                        .get('video_info', {})
                        .get('variants', False)):
                    msg['mp4_url'] = max(data['extended_entities']['media']
                                             [0]['video_info']['variants'],
                                         key=lambda x: x['bitrate']
                                         if x['content_type'] == "video/mp4"
                                         else 0)['url']
        elif data.get('text', False):
            msg['message'] = data['text']
            if data['entities'].get('media', False):
                msg['media_urls'] = [data['entities']['media'][0]['media_url']]
                if (data.get('extended_entities', {})
                        .get('media', [{}])[0]
                        .get('video_info', {})
                        .get('variants', False)):
                    msg['mp4_url'] = max(data['extended_entities']['media']
                                             [0]['video_info']['variants'],
                                         key=lambda x: x['bitrate']
                                         if x['content_type'] == "video/mp4"
                                         else 0)['url']

        if msg['message'][:4] == 'RT @':
            msg['message'] = msg['message'][msg['message'].find(':')+1:]

        return msg
    except Exception, e:
        pp('parse_twitter failed', 'error')
        pp(e, 'error')
        return {}


def check_stream(stream, data):
    # try: data may be empty etc?
    try:
        if stream in data['message'].lower():
            return True
        else:
            return False
    except Exception, e:
        pp('check_stream twitch failed', 'error')
        pp(e)
        return False
