# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:55:12 2016

@author: colinh
"""
#Import the necessary methods from tweepy library
import re
import time
import sys
import multiprocessing
import json

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

		self.l = StdOutListener()
		self.auth = OAuthHandler(config['consumer_token'], config['consumer_secret'])
		self.auth.set_access_token(config['access_token'], config['access_secret'])
		self.api = API(self.auth)
		self.stream = Stream(self.auth, self.l)

		self.strm_con = multiprocessing.Process(target=self.stream_connection, args=([],))

	def stream_connection(self, channel_keys):
		while not self.kill:
			try:
				pp('Twitter Stream died... reconnecting')
				self.stream.filter(track=channel_keys)
			except:
				continue

		self.stream.disconnect()

	def get_twtr_stream_object(self, channel):
		return self.l.channels[channel]

	def refresh_channels(self):
		pp('Refreshing channels...')
		if self.strm_con.is_alive():
			pp('Terminating old connection.')
			self.strm_con.terminate()
			self.stream.disconnect()
		if len(self.l.channels.keys())>0:
			self.strm_con = multiprocessing.Process(target=self.stream_connection, args=(self.l.channels.keys(),))
			self.strm_con.start()
		pp('Refreshed channels.')

	def reset_channels(self):
		pp('Resetting channels...')
		self.l.channels = {}
		if self.strm_con.is_alive():
			pp('Terminating old connection.')
			self.strm_con.terminate()
			self.stream.disconnect()
		pp('Reset channels.')

	def join_channel(self, channel):
		if not channel in self.l.channels.keys():
			pp('Joining channel %s,' % channel)
			self.l.channels[channel] = multiprocessing.Queue()
			if self.strm_con.is_alive():
				pp('Terminating old connection.')
				self.strm_con.terminate()
				self.stream.disconnect()
			self.strm_con = multiprocessing.Process(target=self.stream_connection, args=(self.l.channels.keys(),))
			self.strm_con.start()
			pp('Joining channel.')

	def leave_channel(self, channel):
		if channel in self.l.channels:
			pp('Leaving channel %s,' % channel)
			del self.l.channels[channel]
			if self.strm_con.is_alive():
				pp('Terminating old connection.')
				self.strm_con.terminate()
				self.stream.disconnect()
			if len(self.l.channels.keys()) > 0:
				self.strm_con = multiprocessing.Process(target=self.stream_connection, args=(self.l.channels.keys(),))
				self.strm_con.start()
			else:
				pp('No channels to stream from...')
			pp('Left channel.')
