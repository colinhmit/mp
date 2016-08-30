# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:48:45 2016

@author: colinh
"""

global twitch_config
global master_config

twitch_config = {
	
	# details required to login to twitch IRC server
	'server': 'irc.twitch.tv',
	'port': 6667,
	'username': 'stepthirtytwo',
	'oauth_password': 'oauth:3chiev6dslmp2t4f07ndd7znqm1ygf', # get this from http://twitchapps.com/tmi/
	
	# if set to true will display any data received
	'debug': False,

	# if set to true will log all messages from all channels
	# TODO
	'log_messages': False,

	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 4096
}

server_config = {
	
	# details required to host the server
	'host': 'localhost',
	'port': 4808,
      'listeners' : 10,
	
	# if set to true will display any data received
	'debug': True,

	# if set to true will log all messages from all channels
	# TODO
	'log_messages': False,

	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 4096,
 
      'end_of_chat_data': '//data_sent//'
}

client_config = {
	
	# details required to host the server
	'server': 'localhost',
	'port': 4808,
	
	# if set to true will display any data received
	'debug': False,

	# if set to true will log all messages from all channels
	# TODO
	'log_messages': False,

	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 4096,
 
      'end_of_chat_data': '//data_sent//',
      
      'demo_mode': True
 
}