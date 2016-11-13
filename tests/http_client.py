# import urllib
# import json

# #url = 'https://www.youtube.com/live_comments?action_get_comments=1&video_id=gXJLfBMLeQE&lt=1479069572191551&format=proto&pd=6745&rc=102&scr=true&comment_version=1'

# DEFAULT_YOUTUBE_CHANNEL_INFO_PREFIX = "https://www.youtube.com/live_chat?v=";
# DEFAULT_YOUTUBE_CHANNEL_INFO_POSTFIX = "&dark_theme=1&from_gaming=1&client_version=1.0";

# DEFAULT_YOUTUBE_MESSAGES_PREFIX = "https://www.youtube.com/live_comments?action_get_comments=1&video_id=";
# DEFAULT_YOUTUBE_MESSAGES_INFIX = "&lt=";
# DEFAULT_YOUTUBE_MESSAGES_POSTFIX ="&format=json&comment_version=1";

# lastMessageTime_ = 1479073657001798

# channelName_ = 'jgdQ6hVW3lU'

# channel_info_url = DEFAULT_YOUTUBE_CHANNEL_INFO_PREFIX + channelName_ + DEFAULT_YOUTUBE_CHANNEL_INFO_POSTFIX

# channel_msg_url = DEFAULT_YOUTUBE_MESSAGES_PREFIX + channelName_ + DEFAULT_YOUTUBE_MESSAGES_INFIX + str(lastMessageTime_) + DEFAULT_YOUTUBE_MESSAGES_POSTFIX

# u = urllib.urlopen(channel_info_url)
# v = urllib.urlopen(channel_msg_url)
# # u is a file-like object
# data = u.read()

# data2 = v.read()


import base64
import json
import time
import urllib2
import xml.etree.ElementTree as ET
URL_TEMPLATE = "http://www.youtube.com/live_comments?action_get_comments=1" +\
	"&video_id={video_id}&lt={time}&alt=json&pd=10000" + \
	"&rc={counter}&scr=true&comment_version=1"

class FetchTube:
	def __init__(self, video_id):
		self.last_time = int(time.time())
		self.rc = 0
		self.video_id = video_id
	def fetch(self):
		"""
		returns: tuple of (comments, poll_delay)
		"""
		rc = self.rc
		self.rc += 1
		if self.rc > 5:
			self.rc = 0
		url = URL_TEMPLATE.format(video_id=self.video_id,
			time = self.last_time,
			counter = rc)
		indata=urllib2.urlopen(url)
		outxml = ET.parse(indata)
		print outxml.find("comments").text
		#payload = json.loads(outxml.find("html_content").text)
		self.last_time = payload["latest_time"]
		return payload["comments"], payload["poll_delay"]
		

def get_comments(fetcher):
	while True:
		lastfetch = time.time()
		comments, sleeptime = fetcher.fetch()
		print comments
		for c in comments:
			print c["comment"]
		sltime = min(sleeptime / 1000, 0.2)
		elapsedtime = time.time() - lastfetch
		if elapsedtime < sltime:
			time.sleep(sltime - elapsedtime)


fetcher = FetchTube('jgdQ6hVW3lU')
get_comments(fetcher)