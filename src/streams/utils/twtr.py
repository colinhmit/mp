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
import zmq
import copy
import pickle
import gc
import random

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

from functions_general import *

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
	def __init__(self, input_port):
		self.port = input_port
		self.pipe = None

	def on_data(self, data):
		self.pipe.send_string(data)
		return True

	def on_error(self, status):
		pp(status)

	def on_timeout(self):
		pp('Timeout...')

class twtr:
	def __init__(self, config, init_streams, nlp):
		self.config = config
		self.init_streams = init_streams

		self.streams = self.init_streams

		self.set_twtr_stream_object()

		for _ in xrange(self.config['num_dist_threads']):
			multiprocessing.Process(target=self.distribute).start()

		for _ in xrange(self.config['num_proc_threads']):
			multiprocessing.Process(target=self.process, args=(nlp,)).start()

		if len(self.streams)>0:
			self.stream_conn.start()

	def process(self, nlp):
		context = zmq.Context()
		recvr = context.socket(zmq.PULL)
		recvr.connect("tcp://127.0.0.1:"+str(self.config['zmq_queue_port']))

		sendr = context.socket(zmq.PUB)
		sendr.connect("tcp://127.0.0.1:"+str(self.config['zmq_pub_port']))

		svomap = {}
		svorefresh = random.randint(750, 1000)

		for data in iter(recvr.recv_string, 'STOP'):
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
									'media_url': [jsondata['retweeted_status']['entities']['media'][0]['media_url']],
									'mp4_url': max(jsondata['extended_entities']['media'][0].get('video_info',{}).get('variants',[{'url':'','bitrate':1,'content_type':"video/mp4"}]), key=lambda x:x['bitrate'] if x['content_type']=="video/mp4" else 0)['url'],
									'id': jsondata['id_str']
									}
							else:
								msg = {
									'username': jsondata['user']['name'],
									'message': jsondata['retweeted_status']['text'],
									'media_url': [jsondata['retweeted_status']['entities']['media'][0]['media_url']],
									'mp4_url': '',
									'id': jsondata['id_str']
									}
						else:								
							msg = {
								'username': jsondata['user']['name'],
								'message': jsondata['retweeted_status']['text'],
								'media_url': [jsondata['retweeted_status']['entities']['media'][0]['media_url']],
								'mp4_url': '',
								'id': jsondata['id_str']
								}
					else:
						msg = {
							'username': jsondata['user']['name'],
							'message': jsondata['retweeted_status']['text'],
							'media_url': [],
							'mp4_url': '',
							'id': jsondata['id_str']
							}
			elif 'text' in jsondata:
				if 'media' in jsondata['entities']:
					if 'extended_entities' in jsondata:
						if jsondata['extended_entities']['media'][0].get('video_info',{}).get('variants',[]):
							msg = {
								'username': jsondata['user']['name'],
								'message': jsondata['text'],
								'media_url': [jsondata['entities']['media'][0]['media_url']],
								'mp4_url': max(jsondata['extended_entities']['media'][0].get('video_info',{}).get('variants',[{'url':'','bitrate':1,'content_type':"video/mp4"}]), key=lambda x:x['bitrate'] if x['content_type']=="video/mp4" else 0)['url'],
								'id': jsondata['id_str']
								}
						else:
							msg = {
								'username': jsondata['user']['name'],
								'message': jsondata['text'],
								'media_url': [jsondata['entities']['media'][0]['media_url']],
								'mp4_url': '',
								'id': jsondata['id_str']
								}
					else:
						msg = {
							'username': jsondata['user']['name'],
							'message': jsondata['text'],
							'media_url': jsondata['entities']['media'][0]['media_url'],
							'mp4_url': [],
							'id': jsondata['id_str']
							}
				else:
					msg = {
						'username': jsondata['user']['name'],
						'message': jsondata['text'],
						'media_url': [],
						'mp4_url': '',
						'id': jsondata['id_str']
						}
			if len(msg) > 0:
				hashid = hash(msg['message'])

				if hashid in svomap:
					svos = svomap[hashid]
				else:
					clean_msg = re.sub(r"http\S+", "", msg['message'])
					clean_msg = re.sub(r"[#@]", "", clean_msg)
					clean_msg = re.sub(r"[^\w\s\'\"!.,&?:;_%-]+", "", clean_msg)
					try:
						svos = nlp.parse_text(clean_msg)
					except Exception, e:
						svos = []
					svomap[hashid] = svos

				msg['svos'] = svos

				if len(svomap)>svorefresh:
					svomap = {}
					nlp.flush()
					gc.collect()

				pickled_data = pickle.dumps(msg)
				sendr.send(pickled_data)

	def distribute(self):
		distributing = True

		while distributing:
			try:
				context = zmq.Context(1)
				frontend = context.socket(zmq.SUB)
				frontend.bind("tcp://*:"+str(self.config['zmq_pub_port']))
				frontend.setsockopt(zmq.SUBSCRIBE, "")

				backend = context.socket(zmq.PUB)
				backend.bind("tcp://*:"+str(self.config['zmq_sub_port']))
				zmq.device(zmq.FORWARDER, frontend, backend)
			except Exception, e:
				pp(e)
				
	def set_twtr_stream_object(self):
		config = self.config

		self.l = StdOutListener(config['zmq_queue_port'])
		self.auth = OAuthHandler(config['consumer_token'], config['consumer_secret'])
		self.auth.set_access_token(config['access_token'], config['access_secret'])
		self.api = API(self.auth)
		self.stream_obj = Stream(self.auth, self.l)

		self.stream_conn = multiprocessing.Process(target=self.stream_connection)

	def stream_connection(self):
		context = zmq.Context()
		self.l.pipe = context.socket(zmq.PUSH)
		connected = False
		pp('Starting rebind...')
		while not connected:
			try:
				self.l.pipe.bind("tcp://127.0.0.1:"+str(self.l.port))
				pp('Finished rebinding.')
				connected = True
			except Exception, e:
				pass
		try:
			pp('Connecting to target stream...')
			self.stream_obj.filter(track=self.streams)
			gc.collect()
		except Exception, e:
			pp('/////////////////STREAM CONNECTION WENT DOWN////////////////////')
			pp(e)

	def refresh_streams(self):
		pp('Refreshing streams...')
		if self.stream_conn.is_alive():
			self.stream_obj.disconnect()
 			self.stream_conn.terminate()
		self.stream_conn = multiprocessing.Process(target=self.stream_connection)
		if len(self.streams)>0:
			self.stream_conn.start()

	def reset_streams(self):
		pp('Resetting streams...')
		self.streams = self.init_streams
		if self.stream_conn.is_alive():
			self.stream_obj.disconnect()
 			self.stream_conn.terminate()
		self.stream_conn = multiprocessing.Process(target=self.stream_connection)
		if len(self.streams)>0:
			self.stream_conn.start()

	def join_stream(self, stream):
		if stream not in self.streams:
			pp('Joining stream %s' % stream)
			if self.stream_conn.is_alive():
				self.stream_obj.disconnect()
	 			self.stream_conn.terminate()
			self.streams.append(stream)
			self.stream_conn = multiprocessing.Process(target=self.stream_connection)
			self.stream_conn.start()

	def leave_stream(self, stream):
		if stream in self.streams:
			self.streams.remove(stream)
			if self.stream_conn.is_alive():
				self.stream_obj.disconnect()
	 			self.stream_conn.terminate()
			self.stream_conn = multiprocessing.Process(target=self.stream_connection)
			if len(self.streams)>0:
				self.stream_conn.start()
			else:
				pp('No streams to stream from...')

	def batch_streams(self, streams_to_add, streams_to_remove):
		pp('Batching streams. Adding: '+str(streams_to_add)+', Deleting: '+str(streams_to_remove))
		if self.stream_conn.is_alive():
			self.stream_obj.disconnect()
 			self.stream_conn.terminate()
 		for stream in streams_to_remove:
			if stream in self.streams:
				self.streams.remove(stream)
		for stream in streams_to_add:
			if stream not in self.streams:
				self.streams.append(stream)
		self.stream_conn = multiprocessing.Process(target=self.stream_connection)
		self.stream_conn.start()