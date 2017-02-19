# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:48:45 2016

@author: colinh
"""

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

twitter_config = {
	
	# PRODUCTION TWITTER API
 #    'consumer_token': 'b4pRX7KQPnNQpdyOrC4FTT9Wn',
	# 'consumer_secret': 'GYgrnWSQYzRhD2rCHCXkLLba2bTa0qQ7OCqOGCRB3XShEc4f2d',

	# 'access_token': '784870359241809920-pSQiIXkQXn8miVsqnL6LQrOfzTY7Tix',
	# 'access_secret': 'Olqq3CSWZ5ozLSqRubTIl3AgsCg27tkbfTGLhYAr4lXpd',
                    
	# DEV TWITTER API
    'consumer_token': 'lTImlMFo1GZzqJ5dynMHoOkEK',
	'consumer_secret': 'hkAYOdEN1nqmTtJBszgrC5VZE7gSFtN2nqgFsHxZbl8v8QVR0G',

	'access_token': '805548030816645120-aNstjukeFNVparl3x8lb8dyfUgIQzbf',
	'access_secret': 'QHpVzvSBDPTlQrY4k65ip0k3JFrQRIfKHv8JLUM43QTQw',

	#DEV TWITTER API 2
 #    'consumer_token': 'brULNlsL5AI80FsiMAeH3us42',
	# 'consumer_secret': 'kdPYjOkOIR8NqnXqr7MZvTlR4mPwdMwF80KTytaeHUKFmNCCu5',

	# 'access_token': '178112532-kQ62pLaDjRrPEEn3W7zqsI0tLJgDPMkZgzR0U5iG',
	# 'access_secret': 'eik2jjyu0kLhkr2xNz53182Xa7ayktE646R7XrwQSGuCt',

	#DEV TWITTER API 3
	# 'consumer_token': 'cPOClxrPAOdQhgfQfLdcXZL4D',
	# 'consumer_secret': 'uGByGCcB91FlNizE5edHPuVVmXInXcPIcHKE68n6drh6Achlaq',

	# 'access_token': '815322092627333121-W3OnWqcm8Mh4SGWJJc7OnmChwWump9m',
	# 'access_secret': 'MOMWd6pXkqlKxQQuSosa2fKK4sXqx58w2MhgA9G7OWGUq',

	#Number of distributor threads
	#'num_proc_threads': 25,
	'num_proc_threads': 5,
	'num_dist_threads': 1,

	#ZMQ messaging port
    'zmq_queue_port': 8003,
    'zmq_pub_port': 8004,
    'zmq_sub_port': 8005,

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

      #twitter content cutoff
      'content_max_time': 1800,
      'content_max_size': 20,
                       
	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 4096
}

server_config = {

    'request_host': '',
	'request_port': 8008,

    'data_host': '',
    'twitch_data_port': 8016,
    'twitter_data_port': 8017,
    'featured_data_port': 8018,

    'zmq_subj_port': 8011,
    'zmq_cluster_port': 8012,

    'listeners' : 10,

    #featured
    'twitch_client_id': 'r4jy4y7lwnzoez92z29zlgjlqggdyz',
    'twitch_num_featured': 12,
    'twitter_num_featured': 12,

    #ML clustering
    'subj_pctile': 35,

    #AWS Google API Key
    'sheets_key': '/home/ec2-user/mp/src/config/chrendin_sheets_key.json',

    #DEV Google API Key
    #'sheets_key': '/Users/colinh/Repositories/mp/src/config/chrendin_sheets_key.json',

    #Google API Refs
    'scopes': ['https://www.googleapis.com/auth/spreadsheets.readonly'],
    'spreadsheetID': '1lz4g3-WvT8EjVc2hogalhnGQmkMb1d1fIvatpLUsano',
    'featured_data_range': 'Twitter Featured!A2:E',
    'featured_live_range': 'Twitter Featured!G2',
    'schedule_data_range': 'Scraping Schedule!A2:F',
    'schedule_live_range': 'Scraping Schedule!H2',

    #AWS Log Path
    'twitter_log_path': '/home/ec2-user/mp/src/logs/twitter/',
    'twitch_log_path': '/home/ec2-user/mp/src/logs/twitch/',

    #DEV Log Path
    # 'twitter_log_path': '/Users/colinh/Repositories/mp/src/logs/twitter/',
    # 'twitch_log_path': '/Users/colinh/Repositories/mp/src/logs/twitch/',

	#Target stream allowed channels
	'target_streams': ['trump'],

	# if set to true will display any data received
	'debug': False,

	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 4096,
	'socket_send_size': 4000
}

client_config = {

    'host': '127.0.0.1',

    #AWS Settings
    # 'port': 80,
    # 'request_host': '35.160.61.218',
    # 'data_host': '35.160.61.218',

    #DEV Hosts
    'request_host': '127.0.0.1',
    'data_host': '127.0.0.1',
    'port': 80,

    # #AWS DEV Hosts
    # 'request_host': '35.166.70.54',
    # 'data_host': '35.166.70.54',
    # 'port': 80,	

    #Ports
    'request_port': 8008,
    'twitch_data_port': 8016,
    'twitter_data_port': 8017,
    'featured_data_port': 8018,

    # if set to true will display any data received
    'debug': False,

    # maximum amount of bytes to receive from socket - 1024-4096 recommended
    'socket_buffer_size': 4096,
    'socket_send_size': 4000
}
