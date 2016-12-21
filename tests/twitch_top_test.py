import requests
import json
import sys

sys.path.append('/Users/colinh/Repositories/mp/src')

import streams.utils.twtr as twtr_
from config.universal_config import *

#twitch
oauth_password= 'oauth:1a6qgh8wz0b0lb2ue5zenht2lrkcdx' # get this from http://twitchapps.com/tmi/

client_id= 'r4jy4y7lwnzoez92z29zlgjlqggdyz'
headers = {'Accept':'application/vnd.twitchtv.v3+json', 'Client-ID':client_id}

r = requests.get('https://api.twitch.tv/kraken/streams/featured', headers = headers)
#r contains all

r2 = json.loads(r.content)
r2 = r2['featured']

a=[{'stream':x['stream']['channel']['name'], 'image': x['stream']['preview']['medium'], 'description': x['title'], 'viewers': x['stream']['viewers']} for x in r2]



#twitter
twit = twtr_.twtr(twitter_config)
trends1 = twit.api.trends_place(1)