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
	'username': 'stepthirtytwo',
	'oauth_password': 'oauth:3chiev6dslmp2t4f07ndd7znqm1ygf', # get this from http://twitchapps.com/tmi/
	
	# if set to true will display any data received
	'debug': True,

	# if set to true will log all messages from all channels
	# TODO
	'log_messages': False,

      #fw_eo output from funcions_matching threshold 
      'fw_eo_threshold': 65,
      
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

      'log_path': '/Users/colinh/Repositories/mp/stream/backtest/',
                       
	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 4096
}

global server_config

server_config = {
	
	# details required to host the server
     'host': '127.0.0.1',
    	#'host': 'localhost',
     #'host': '192.168.0.19',
	'port': 4808,
      'listeners' : 10,
	
	# if set to true will display any data received
	'debug': True,

	# if set to true will log all messages from all channels
	# TODO
	'log_messages': False,

	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 4096,
 
      'end_of_data': '//data_sent//'
}

global client_config

client_config = {
	
	# details required to host the server
	'default_server': '127.0.0.1',
	'port': 4808,
	
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
