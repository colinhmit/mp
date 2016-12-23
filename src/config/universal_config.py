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
	'client_id': 'r4jy4y7lwnzoez92z29zlgjlqggdyz',
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
      'matched_init_base': 50,
      'matched_add_base': 15,
      'matched_add_user_base':500,

      'buffer_mult': 4,
      
      'decay_msg_base': 1,
      'decay_msg_min_limit': 0.4,
      'decay_time_mtch_base': 4,
      'decay_time_base': 0.2,
                       
	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 4096
}

global twitter_config

twitter_config = {
	
	# details required to login to twitter stream API
 #     'consumer_token': 'b4pRX7KQPnNQpdyOrC4FTT9Wn',
	#  'consumer_secret': 'GYgrnWSQYzRhD2rCHCXkLLba2bTa0qQ7OCqOGCRB3XShEc4f2d',

	# 'access_token': '784870359241809920-pSQiIXkQXn8miVsqnL6LQrOfzTY7Tix',
	# 'access_secret': 'Olqq3CSWZ5ozLSqRubTIl3AgsCg27tkbfTGLhYAr4lXpd',
                    
	# #FALL BACK TWITTER API
    'consumer_token': 'brULNlsL5AI80FsiMAeH3us42',
	'consumer_secret': 'kdPYjOkOIR8NqnXqr7MZvTlR4mPwdMwF80KTytaeHUKFmNCCu5',

	'access_token': '178112532-kQ62pLaDjRrPEEn3W7zqsI0tLJgDPMkZgzR0U5iG',
	'access_secret': 'eik2jjyu0kLhkr2xNz53182Xa7ayktE646R7XrwQSGuCt',

	# #2nd FALL BACK TWITTER API
 #    'consumer_token': 'lTImlMFo1GZzqJ5dynMHoOkEK',
	# 'consumer_secret': 'hkAYOdEN1nqmTtJBszgrC5VZE7gSFtN2nqgFsHxZbl8v8QVR0G',

	# 'access_token': '805548030816645120-aNstjukeFNVparl3x8lb8dyfUgIQzbf',
	# 'access_secret': 'QHpVzvSBDPTlQrY4k65ip0k3JFrQRIfKHv8JLUM43QTQw',

	# if set to true will display any data received
	'debug': False,

	# if set to true will log all messages from all channels
	# TODO
	'log_messages': False,

	#fw_eo output from funcions_matching threshold 
	'fo_compare_threshold': 65,
  	'so_compare_threshold': 80,
      
     #twitter trending params
      'matched_init_base': 50,
      'matched_add_base': 15,
      'matched_add_user_base': 500,
      
      'buffer_mult': 4,

      'decay_msg_base': 1,
      'decay_msg_min_limit': 0.4,
      'decay_time_mtch_base': 4,
      'decay_time_base': 0.2,
                       
	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 4096
}

global server_config

server_config = {
	
	# details required to host the server

    'host': '172.31.4.69',
    'port': 80,
    #'host': '127.0.0.1',
    #'port': 4808,

    #featured
    'twitch_client_id': 'r4jy4y7lwnzoez92z29zlgjlqggdyz',

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