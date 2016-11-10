# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:55:12 2016

@author: colinh
"""
#Import the necessary methods from tweepy library
import re
import time
import sys
import thread
import json
import Queue

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from functions_general import *

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
	def __init__(self):
		self.channels = {}

	def on_data(self, data):
		jsondata = json.loads(data)
		if 'text' in jsondata.keys():
			for key in self.channels.keys():
				if key.lower() in jsondata['text'].lower():
					#NEED TO FILTER HASHTAGS!
					msg = {
						'channel': key,
						'username': jsondata['user']['name'],
						'message': jsondata['text']
					}
					self.channels[key].put(msg)
		return True

	def on_error(self, status):
		print status

class twtr:
	def __init__(self, config):
		self.config = config
		self.set_twtr_stream_object()

	def set_twtr_stream_object(self):
		config = self.config

		self.l = StdOutListener()
		auth = OAuthHandler(config['consumer_token'], config['consumer_secret'])
		auth.set_access_token(config['access_token'], config['access_secret'])
		self.stream = Stream(auth, self.l)

	def get_twtr_stream_object(self, channel):
		return self.l.channels[channel]

	def join_channel(self, channel):
		if not channel in self.l.channels.keys():
			pp('Joining channel %s,' % channel)
			self.l.channels[channel] = Queue.Queue()
			self.stream.disconnect()
			self.stream.filter(track=self.l.channels.keys(), async=1)
			pp('Joining channel.')

	def leave_channel(self, channel):
		if channel in self.l.channels:
			pp('Leaving channel %s,' % channel)
			del self.l.channels[channel]
			self.stream.disconnect()
			if len(self.l.channels.keys()) > 0:
				self.stream.filter(track=self.l.channels.keys(), async=1)
			else:
				pp('No channels to stream from...')
			pp('Left channel.')
