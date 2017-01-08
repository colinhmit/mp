# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:55:12 2016

@author: colinh
"""
#Import the necessary methods from tweepy library
import re
import time
import sys
import threading
import Queue
import json
import multiprocessing

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
		if 'retweeted_status' in jsondata.keys():
			if 'text' in jsondata['retweeted_status'].keys():
				if 'media' in jsondata['retweeted_status']['entities'].keys():
					msg = {
						'username': jsondata['user']['name'],
						'message': jsondata['retweeted_status']['text'],
						'media_url': jsondata['retweeted_status']['entities']['media'][0]['media_url']
						}
				else:
					msg = {
						'username': jsondata['user']['name'],
						'message': jsondata['retweeted_status']['text'],
						'media_url': ''
						}
				for key in self.channels.keys():
					self.channels[key].put(msg)
		elif 'text' in jsondata.keys():
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

		self.hose_l = StdOutListener()
		self.hose_auth = OAuthHandler(config['hose_consumer_token'], config['hose_consumer_secret'])
		self.hose_auth.set_access_token(config['hose_access_token'], config['hose_access_secret'])
		self.hose_api = API(self.hose_auth)
		self.hose_stream = Stream(self.hose_auth, self.hose_l)

		self.target_l = StdOutListener()
		self.target_auth = OAuthHandler(config['target_consumer_token'], config['target_consumer_secret'])
		self.target_auth.set_access_token(config['target_access_token'], config['target_access_secret'])
		self.target_api = API(self.target_auth)
		self.target_stream = Stream(self.target_auth, self.target_l)

		self.target_conn = multiprocessing.Process(target=self.target_stream_connection, args=([],))
		self.hose_conn = threading.Thread(target=self.hose_stream_connection).start()

	def hose_stream_connection(self):
		while not self.kill:
			try:
				pp('Twitter Stream died... reconnecting')
				self.hose_stream.sample()
			except:
				continue

		self.stream.disconnect()

	def target_stream_connection(self, channel_keys):
		while not self.kill:
			try:
				pp('Twitter Stream died... reconnecting')
				self.target_stream.filter(track=channel_keys)
			except:
				continue

		self.stream.disconnect()

	def get_twtr_hose_stream_object(self, channel):
		return self.hose_l.channels[channel]

	def get_twtr_target_stream_object(self, channel):
		return self.target_l.channels[channel]

	def refresh_stream(self):
		pp('Refreshing channels...')
		self.kill = True
		self.kill = False
		self.hose_stream.disconnect()
		if self.target_conn.is_alive():
			pp('Terminating old connection.')
			self.target_conn.terminate()
			self.target_stream.disconnect()
		if len(self.target_l.channels.keys())>0:
			self.target_conn = multiprocessing.Process(target=self.target_stream_connection, args=(self.target_l.channels.keys(),))
			self.target_conn.start()
		self.hose_conn = threading.Thread(target=self.hose_stream_connection).start()
		pp('Refreshed channels.')

	def reset_channels(self):
		pp('Resetting channels...')
		self.target_l.channels = {}
		self.hose_l.channels = {}
		if self.target_conn.is_alive():
			pp('Terminating old connection.')
			self.target_conn.terminate()
			self.target_stream.disconnect()
		pp('Reset channels.')

	def join_hose_channel(self, channel):
		if not channel in self.hose_l.channels.keys():
			pp('Joining channel %s' % channel)
			self.hose_l.channels[channel] = Queue.Queue()
			pp('Joining channel.')

	def join_target_channel(self, channel):
		if not channel in self.target_l.channels.keys():
			pp('Joining channel %s,' % channel)
			self.target_l.channels[channel] = multiprocessing.Queue()
			if self.target_conn.is_alive():
				pp('Terminating old connection.')
				self.target_conn.terminate()
				self.target_stream.disconnect()
			self.target_conn = multiprocessing.Process(target=self.target_stream_connection, args=(self.target_l.channels.keys(),))
			self.target_conn.start()
			pp('Joining channel.')

	def leave_hose_channel(self, channel):
		if channel in self.hose_l.channels:
			pp('Leaving channel %s' % channel)
			del self.hose_l.channels[channel]
			pp('Left channel.')

	def leave_target_channel(self, channel):
		if channel in self.target_l.channels:
			pp('Leaving channel %s,' % channel)
			del self.target_l.channels[channel]
			if self.target_conn.is_alive():
				pp('Terminating old connection.')
				self.target_conn.terminate()
				self.target_stream.disconnect()
			if len(self.target_l.channels.keys())>0:
				self.target_conn = multiprocessing.Process(target=self.target_stream_connection, args=(self.target_l.channels.keys(),))
				self.target_conn.start()
			else:
				pp('No channels to stream from...')
			pp('Left channel.')
