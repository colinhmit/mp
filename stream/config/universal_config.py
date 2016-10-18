# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:48:45 2016

@author: colinh
"""

global twitch_config

twitch_config = {
	
	# details required to login to twitch IRC server
	'server': 'irc.twitch.tv',
	'port': 6667,
	'username': 'chrendin',
	'oauth_password': 'oauth:1a6qgh8wz0b0lb2ue5zenht2lrkcdx', # get this from http://twitchapps.com/tmi/
	
	# if set to true will display any data received
	'debug': False,

	# if set to true will log all messages from all channels
	# TODO
	'log_messages': False,

	  #fw_eo output from funcions_matching threshold 
	  'fo_compare_threshold': 65,
  	'so_compare_threshold': 80,
      
      #twitch_stream trending params
      'matched_init_base': 20,
      'matched_add_base': 20,
      
      'decay_msg_base': 1,
      'decay_time_base': 1,
                       
	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 4096
}


global twitch_scraper_config

twitch_scraper_config = {
	
	# details required to login to twitch IRC server
	'server': 'irc.twitch.tv',
	'port': 6667,
	'username': 'stepthirtytwo',
	'oauth_password': 'oauth:3chiev6dslmp2t4f07ndd7znqm1ygf', # get this from http://twitchapps.com/tmi/
	
	# if set to true will display any data received
	'debug': True,

	# if set to true will log all messages from all channels
	# TODO
	'log_messages': False,

      'log_path': '/Users/colinh/Repositories/mp/stream/backtest/logs/',
                       
	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 4096
}

global server_config

server_config = {
	
	# details required to host the server

    'host': '172.31.4.69',
    'port': 80,
    #'host': 'localhost',
    #'host': '192.168.0.19',

	# if set to true will display any data received
	'debug': False,

	# if set to true will log all messages from all channels
	# TODO
	'log_messages': False,

	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 4096,

	#messaging mode
	#'mode' : 'python'
	#'mode': 'sqs',
	'mode': 'multicast',
 
    'end_of_data': '//data_sent//'
}

global client_config

client_config = {
	
	# details required to host the server
	'default_server': '127.0.0.1',
	'multicast_server': '239.192.1.100',
	'port': 4808,
    'ttl': 32,
	
	# if set to true will display any data received
	'debug': False,

	# if set to true will log all messages from all channels
	# TODO
	'log_messages': False,

	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 4096,
 
      'end_of_data': '//data_sent//',
      
      #modes: backtest, demo
      'mode': 'demo'
 
}
