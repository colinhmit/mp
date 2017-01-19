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
	
	#HOSE TWITTER API
    'hose_consumer_token': 'b4pRX7KQPnNQpdyOrC4FTT9Wn',
	'hose_consumer_secret': 'GYgrnWSQYzRhD2rCHCXkLLba2bTa0qQ7OCqOGCRB3XShEc4f2d',

	'hose_access_token': '784870359241809920-pSQiIXkQXn8miVsqnL6LQrOfzTY7Tix',
	'hose_access_secret': 'Olqq3CSWZ5ozLSqRubTIl3AgsCg27tkbfTGLhYAr4lXpd',
                    
	#TARGET TWITTER API
    'target_consumer_token': 'lTImlMFo1GZzqJ5dynMHoOkEK',
	'target_consumer_secret': 'hkAYOdEN1nqmTtJBszgrC5VZE7gSFtN2nqgFsHxZbl8v8QVR0G',

	'target_access_token': '805548030816645120-aNstjukeFNVparl3x8lb8dyfUgIQzbf',
	'target_access_secret': 'QHpVzvSBDPTlQrY4k65ip0k3JFrQRIfKHv8JLUM43QTQw',

	#DEV HOSE TWITTER API
 #    'hose_consumer_token': 'brULNlsL5AI80FsiMAeH3us42',
	# 'hose_consumer_secret': 'kdPYjOkOIR8NqnXqr7MZvTlR4mPwdMwF80KTytaeHUKFmNCCu5',

	# 'hose_access_token': '178112532-kQ62pLaDjRrPEEn3W7zqsI0tLJgDPMkZgzR0U5iG',
	# 'hose_access_secret': 'eik2jjyu0kLhkr2xNz53182Xa7ayktE646R7XrwQSGuCt',

	#DEV TARGET TWITTER API
	# 'target_consumer_token': 'cPOClxrPAOdQhgfQfLdcXZL4D',
	# 'target_consumer_secret': 'uGByGCcB91FlNizE5edHPuVVmXInXcPIcHKE68n6drh6Achlaq',

	# 'target_access_token': '815322092627333121-W3OnWqcm8Mh4SGWJJc7OnmChwWump9m',
	# 'target_access_secret': 'MOMWd6pXkqlKxQQuSosa2fKK4sXqx58w2MhgA9G7OWGUq',

	#Target stream allowed channels
	'target_streams': ['trump'],

	#Number of distributor threads
	'num_dist_threads': 100,

	# if set to true will display any data received
	'debug': False,

	#fw_eo output from funcions_matching threshold 
	'fo_compare_threshold': 65,
  	'so_compare_threshold': 80,

  	#svo thresholds
  	'subj_compare_threshold': 85,
  	'verb_compare_threshold': 0.3,
  	'obj_compare_threshold': 0.5,
      
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

    'request_host': '',
	'request_port': 8008,

    'data_host': '',
    'data_port': 8007,

    'listeners' : 10,

    #featured
    'twitch_client_id': 'r4jy4y7lwnzoez92z29zlgjlqggdyz',

	# if set to true will display any data received
	'debug': False,

	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 4096,
	'socket_send_size': 4000
}

global client_config

client_config = {

    'host': '127.0.0.1',

    #AWS Settings
    'port': 80,
    'request_host': '35.160.61.218',
    'data_host': '35.160.61.218',

    #DEV Hosts
    # 'request_host': '127.0.0.1',
    # 'data_host': '127.0.0.1',
    # 'port': 4808,

    #Ports
    'request_port': 8008,
    'data_port': 8007,

    # if set to true will display any data received
    'debug': False,

    # maximum amount of bytes to receive from socket - 1024-4096 recommended
    'socket_buffer_size': 4096,
    'socket_send_size': 4000
}
