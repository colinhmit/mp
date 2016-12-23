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
import threading
import json
import Queue

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

from functions_general import *

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
	def __init__(self):
		self.channels = {}

	def on_data(self, data):
		jsondata = json.loads(data)
		if 'text' in jsondata.keys():
			pp('/////DEBUGGING//////')
			pp(jsondata['text'])
			pp(jsondata['entities'])
			if 'media' in jsondata['entities'].keys():
				msg = {
					'username': jsondata['user']['name'],
					'message': jsondata['text'],
					'media_url': jsondata['entities']['media'][0]['media_url']
					}
			else:
				msg = {
					'username': jsondata['user']['name'],
					'message': jsondata['text'],
					'media_url': ''
					}	
			for key in self.channels.keys():
				self.channels[key].put(msg)
		return True

	def on_error(self, status):
		pp(status)

	def on_timeout(self):
		pp('Timeout...')

class twtr:
	def __init__(self, config):
		self.config = config
		self.kill = False
		self.set_twtr_stream_object()
		
	def set_twtr_stream_object(self):
		config = self.config

		self.l = StdOutListener()
		self.auth = OAuthHandler(config['consumer_token'], config['consumer_secret'])
		self.auth.set_access_token(config['access_token'], config['access_secret'])
		self.api = API(self.auth)

	def stream_connection(self, channel_keys):
		while not self.kill:
			try:
				self.stream = Stream(self.auth, self.l)
				self.stream.filter(track=channel_keys)
			except:
				continue

		self.stream.disconnect()

	def get_twtr_stream_object(self, channel):
		return self.l.channels[channel]

	def refresh_channels(self):
		pp('Refreshing channels...')
		self.kill = True
		self.kill = False
		threading.Thread(target=self.stream_connection, args=(self.l.channels.keys(),)).start()
		pp('Refreshed channels.')

	def reset_channels(self):
		pp('Resetting channels...')
		self.l.channels = {}
		self.kill = True
		pp('Reset channels.')

	def join_channel(self, channel):
		if not channel in self.l.channels.keys():
			pp('Joining channel %s,' % channel)
			self.l.channels[channel] = Queue.Queue()
			self.kill = True
			self.kill = False
			threading.Thread(target=self.stream_connection, args=(self.l.channels.keys(),)).start()
			pp('Joining channel.')

	def leave_channel(self, channel):
		if channel in self.l.channels:
			pp('Leaving channel %s,' % channel)
			del self.l.channels[channel]
			self.kill = True
			if len(self.l.channels.keys()) > 0:
				self.kill = False
				threading.Thread(target=self.stream_connection, args=(self.l.channels.keys(),)).start()
			else:
				pp('No channels to stream from...')
			pp('Left channel.')
