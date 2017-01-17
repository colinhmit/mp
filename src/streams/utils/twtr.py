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
import datetime

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

from functions_general import *

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
	def __init__(self, queue):
		self.queue = queue

	def on_data(self, data):
		self.queue.put(data)
		return True

	def on_error(self, status):
		pp(status)

	def on_timeout(self):
		pp('Timeout...')

class twtr:
	def __init__(self, config):
		self.config = config
		self.kill = False
		self.input_queue = multiprocessing.JoinableQueue()
		self.streams = {}
		self.target_streams = []

		self.streams['trump'] = Queue.Queue()
		self.target_streams = ['trump']

		self.distribute_thread = threading.Thread(target = self.distribute).start()
		self.set_twtr_stream_object()

	def distribute(self):
		for data in iter(self.input_queue.get, 'STOP'):
			jsondata = json.loads(data)
			msg = {}
			if 'retweeted_status' in jsondata:
				if 'text' in jsondata['retweeted_status']:
					if 'media' in jsondata['retweeted_status']['entities']:
						if 'extended_entities' in jsondata:
							if jsondata['extended_entities']['media'][0].get('video_info',{}).get('variants',[]):
								msg = {
									'username': jsondata['user']['name'],
									'message': jsondata['retweeted_status']['text'],
									'media_url': '',
									'mp4_url': max(jsondata['extended_entities']['media'][0].get('video_info',{}).get('variants',[{'url':'','bitrate':1,'content_type':"video/mp4"}]), key=lambda x:x['bitrate'] if x['content_type']=="video/mp4" else 0)['url']
									}
							else:
								msg = {
									'username': jsondata['user']['name'],
									'message': jsondata['retweeted_status']['text'],
									'media_url': jsondata['retweeted_status']['entities']['media'][0]['media_url'],
									'mp4_url': ''
									}
						else:								
							msg = {
								'username': jsondata['user']['name'],
								'message': jsondata['retweeted_status']['text'],
								'media_url': jsondata['retweeted_status']['entities']['media'][0]['media_url'],
								'mp4_url': ''
								}
					else:
						msg = {
							'username': jsondata['user']['name'],
							'message': jsondata['retweeted_status']['text'],
							'media_url': '',
							'mp4_url': ''
							}
			elif 'text' in jsondata:
				if 'media' in jsondata['entities']:
					if 'extended_entities' in jsondata:
						if jsondata['extended_entities']['media'][0].get('video_info',{}).get('variants',[]):
							msg = {
								'username': jsondata['user']['name'],
								'message': jsondata['text'],
								'media_url': '',
								'mp4_url': max(jsondata['extended_entities']['media'][0].get('video_info',{}).get('variants',[{'url':'','bitrate':1,'content_type':"video/mp4"}]), key=lambda x:x['bitrate'] if x['content_type']=="video/mp4" else 0)['url']
								}
						else:
							msg = {
								'username': jsondata['user']['name'],
								'message': jsondata['text'],
								'media_url': jsondata['entities']['media'][0]['media_url'],
								'mp4_url': ''
								}
					else:
						msg = {
							'username': jsondata['user']['name'],
							'message': jsondata['text'],
							'media_url': jsondata['entities']['media'][0]['media_url'],
							'mp4_url': ''
							}
				else:
					msg = {
						'username': jsondata['user']['name'],
						'message': jsondata['text'],
						'media_url': '',
						'mp4_url': ''
						}
			if len(msg) > 0:
				for key in self.streams.keys():
					self.streams[key].put(msg)
			self.input_queue.task_done()

	def set_twtr_stream_object(self):
		config = self.config

		self.hose_l = StdOutListener(self.input_queue)
		self.hose_auth = OAuthHandler(config['hose_consumer_token'], config['hose_consumer_secret'])
		self.hose_auth.set_access_token(config['hose_access_token'], config['hose_access_secret'])
		self.hose_api = API(self.hose_auth)
		self.hose_stream = Stream(self.hose_auth, self.hose_l)

		self.target_l = StdOutListener(self.input_queue)
		self.target_auth = OAuthHandler(config['target_consumer_token'], config['target_consumer_secret'])
		self.target_auth.set_access_token(config['target_access_token'], config['target_access_secret'])
		self.target_api = API(self.target_auth)
		self.target_stream = Stream(self.target_auth, self.target_l)

		self.target_conn = multiprocessing.Process(target=self.target_stream_connection)
		self.target_conn.start()
		self.hose_conn = threading.Thread(target=self.hose_stream_connection).start()

	def hose_stream_connection(self):
		while not self.kill:
			try:
				pp('Hose Twitter Stream died... reconnecting')
				self.hose_stream.sample()
			except:
				continue

		self.stream.disconnect()

	def target_stream_connection(self):
		while not self.kill:
			try:
				pp('Target Twitter Stream died... reconnecting')
				self.target_stream.filter(track=self.target_streams)
			except:
				continue

		self.stream.disconnect()

	def get_twtr_stream_object(self, stream):
		return self.streams[stream]

	def refresh_streams(self):
		pp('Refreshing streams...')
		self.kill = True
		self.kill = False
		self.hose_stream.disconnect()
		if self.target_conn.is_alive():
			pp('Terminating old connection.')
			self.target_conn.terminate()
			self.target_stream.disconnect()
		if len(self.target_streams)>0:
			self.target_conn = multiprocessing.Process(target=self.target_stream_connection)
			self.target_conn.start()
		self.hose_conn = threading.Thread(target=self.hose_stream_connection).start()
		pp('Refreshed streams.')

	def reset_streams(self):
		pp('Resetting streams...')
		self.streams = {}
		self.target_streams = []
		if self.target_conn.is_alive():
			pp('Terminating old connection.')
			self.target_conn.terminate()
			self.target_stream.disconnect()
		pp('Reset streams.')

	def join_stream(self, stream, target):
		if not stream in self.streams:
			pp('Joining stream %s' % stream)
			self.streams[stream] = Queue.Queue()
			if target:
				self.target_streams.append(stream)
				if self.target_conn.is_alive():
					pp('Terminating old connection.')
					self.target_conn.terminate()
					self.target_stream.disconnect()
				self.target_conn = multiprocessing.Process(target=self.target_stream_connection)
				self.target_conn.start()
			pp('Joining stream.')

	def leave_stream(self, stream):
		if stream in self.streams:
			pp('Leaving stream %s' % stream)
			del self.streams[stream]
			pp('Left hose stream.')
			if stream in self.target_streams:
				self.target_streams.remove(stream)
				if self.target_conn.is_alive():
					pp('Terminating old connection.')
					self.target_conn.terminate()
					self.target_stream.disconnect()
				if len(self.target_streams)>0:
					self.target_conn = multiprocessing.Process(target=self.target_stream_connection)
					self.target_conn.start()
				else:
					pp('No streams to stream from...')
				pp('Left target stream.')
