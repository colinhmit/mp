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
	def __init__(self, config, init_streams):
		self.config = config
		self.input_queue = Queue.Queue()
		self.streams = {}

		for stream in init_streams:
			self.streams[stream] = Queue.Queue()

		for _ in xrange(self.config['num_dist_threads']):
			threading.Thread(target = self.distribute).start()

		self.set_twtr_stream_object()

	def distribute(self):
		for data in iter(self.input_queue.get, 'STOP'):
			pp(self.input_queue.qsize())
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

	def set_twtr_stream_object(self):
		config = self.config

		self.l = StdOutListener(self.input_queue)
		self.auth = OAuthHandler(config['consumer_token'], config['consumer_secret'])
		self.auth.set_access_token(config['access_token'], config['access_secret'])
		self.api = API(self.auth)
		self.stream_obj = Stream(self.target_auth, self.target_l)

		self.stream_conn = threading.Thread(target=self.stream_connection)

	def stream_connection(self):
		try:
			pp('Connecting to target stream...')
			self.stream_obj.filter(track=self.streams.keys())
		except Exception, e:
			pp(e)

	def get_twtr_stream_object(self, stream):
		return self.streams[stream]

	def refresh_streams(self):
		pp('Refreshing streams...')
		self.stream_conn.disconnect()
		self.stream_conn = threading.Thread(target=self.stream_connection)
		if len(self.streams)>0:
			self.stream_conn.start()

	def reset_streams(self):
		pp('Resetting streams...')
		self.streams = {}
		self.stream_conn.disconnect()
		self.stream_conn = threading.Thread(target=self.stream_connection)
		if len(self.streams)>0:
			self.stream_conn.start()

	def join_stream(self, stream):
		if stream not in self.streams:
			pp('Joining stream %s' % stream)
			self.stream_conn.disconnect()
			self.streams[stream] = Queue.Queue()
			self.stream_conn = threading.Thread(target=self.stream_connection)
			self.stream_conn.start()

	def leave_stream(self, stream):
		if stream in self.streams:
			del self.streams[stream]
			self.stream_conn.disconnect()
			self.stream_conn = threading.Thread(target=self.stream_connection)
			if len(self.streams)>0:
				self.stream_conn.start()
			else:
				pp('No streams to stream from...')

	def batch_streams(self, streams_to_add):
		pp('Batching streams.')
		self.streams = {}
		self.stream_conn.disconnect()
		for stream in streams_to_add:
			self.streams[stream] = Queue.Queue()
		self.stream_conn = threading.Thread(target=self.stream_connection)
		self.stream_conn.start()