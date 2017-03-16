# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:48:45 2016

@author: colinh
"""

input_config = {
    'zmq_input_host': '127.0.0.1',
    'zmq_proc_host': '127.0.0.1',
    'zmq_stream_host': '127.0.0.1',

    # ZMQ ports
    'zmq_irc_input_port': 8002,
    'zmq_twtr_input_port': 8003,
    'zmq_rddt_input_port': 8004,

    'zmq_irc_proc_port': 8012,
    'zmq_twtr_proc_port': 8013,
    'zmq_rddt_proc_port': 8014,

    'zmq_irc_output_port': 8022,
    'zmq_twtr_output_port': 8023,
    'zmq_rddt_output_port': 8024,

    # Number of processing threads
    'num_irc_procs': 25,
    'num_twtr_procs': 30,
    'num_rddt_procs': 25,

    'blacklinks': ['rocksroman12.net', 'lovesomething24.com', 'worldtruepic.me', 'dashingsumit.mobi'],

    # IRC Config
    'irc_config': {
        # Attributes
        'self': 'twitch',

        # ZMQ messaging port
        'zmq_host': '127.0.0.1',
        'zmq_port': 8002,

        # Production Twitch IRC Login    
        'server': 'irc.twitch.tv',
        'port': 6667,
        'username': 'chrendin',
        'client_id': 'r4jy4y7lwnzoez92z29zlgjlqggdyz',
        'oauth_password': 'oauth:1a6qgh8wz0b0lb2ue5zenht2lrkcdx',
        'socket_buffer_size': 4096
    },

    # TWTR Config
    'twtr_config': {
        # Attributes
        'self': 'twitter',

        # ZMQ messaging port
        'zmq_host': '127.0.0.1',
        'zmq_port': 8003,

        # Production Twitter API Login
        # 'consumer_token': 'b4pRX7KQPnNQpdyOrC4FTT9Wn',
        # 'consumer_secret': 'GYgrnWSQYzRhD2rCHCXkLLba2bTa0qQ7OCqOGCRB3XShEc4f2d',
        # 'access_token': '784870359241809920-pSQiIXkQXn8miVsqnL6LQrOfzTY7Tix',
        # 'access_secret': 'Olqq3CSWZ5ozLSqRubTIl3AgsCg27tkbfTGLhYAr4lXpd',
                        
        # AWS DEV Twitter API Login
        'consumer_token': 'lTImlMFo1GZzqJ5dynMHoOkEK',
        'consumer_secret': 'hkAYOdEN1nqmTtJBszgrC5VZE7gSFtN2nqgFsHxZbl8v8QVR0G',
        'access_token': '805548030816645120-aNstjukeFNVparl3x8lb8dyfUgIQzbf',
        'access_secret': 'QHpVzvSBDPTlQrY4k65ip0k3JFrQRIfKHv8JLUM43QTQw',

        # Dev #2 Twitter API Login
        # 'consumer_token': 'brULNlsL5AI80FsiMAeH3us42',
        # 'consumer_secret': 'kdPYjOkOIR8NqnXqr7MZvTlR4mPwdMwF80KTytaeHUKFmNCCu5',
        # 'access_token': '178112532-kQ62pLaDjRrPEEn3W7zqsI0tLJgDPMkZgzR0U5iG',
        # 'access_secret': 'eik2jjyu0kLhkr2xNz53182Xa7ayktE646R7XrwQSGuCt'

        # Dev #3 Twitter API Login
        # 'consumer_token': 'cPOClxrPAOdQhgfQfLdcXZL4D',
        # 'consumer_secret': 'uGByGCcB91FlNizE5edHPuVVmXInXcPIcHKE68n6drh6Achlaq',
        # 'access_token': '815322092627333121-W3OnWqcm8Mh4SGWJJc7OnmChwWump9m',
        # 'access_secret': 'MOMWd6pXkqlKxQQuSosa2fKK4sXqx58w2MhgA9G7OWGUq',
    },

    'rddt_config': {
        # Attributes
        'self': 'reddit',

        # ZMQ messaging
        'zmq_host': '127.0.0.1',
        'zmq_port': 8004,

        # Reddit API Login
        'client_token': 'bx_HkZiUhuYJCw',
        'client_secret': '5l9swqgf2tAY2je0i61pNklgOCg',
        'user_agent': 'ISS:staycurrents.com:v0.1.9 (by /u/staycurrents)'
    }

}

stream_config = {
    # DEV ZMQ hosts
    'zmq_http_host': '127.0.0.1',
    # ZMQ messaging ports
    'zmq_http_port': 8081,

    'twitch_featured':{
        'self': 'twitch',
        'twitch_client_id': 'r4jy4y7lwnzoez92z29zlgjlqggdyz',
        'num_featured': 12,
        'refresh_featured_timeout': 1200,
        'gc_timeout': 300
    },
    
    'twitter_featured':{
        'self': 'twitter',
        'num_featured': 12,
        'featured_buffer_maxlen': 100,
        'refresh_featured_timeout': 1200,
        'gc_timeout': 300
    },

    'reddit_featured':{
        'self': 'reddit',
        'refresh_featured_timeout': 1200,
        'gc_timeout': 300
    },
    
    'google_sheets':{
        #AWS Google API Key
        'sheets_key': '/home/ec2-user/mp/src/config/chrendin_sheets_key.json',
        #DEV Google API Key
        #'sheets_key': '/Users/colinh/Repositories/mp/src/config/chrendin_sheets_key.json',
        'scopes': ['https://www.googleapis.com/auth/spreadsheets.readonly'],
        'spreadsheetID': '1lz4g3-WvT8EjVc2hogalhnGQmkMb1d1fIvatpLUsano',
        'featured_data_range': 'Twitter Featured!A2:E',
        'featured_live_range': 'Twitter Featured!G2'
    },

    # Twitch Stream Config
    'twitch_config': {
        # Attributes
        'self': 'twitch',
        'debug': False,

        # DEV ZMQ hosts
        'zmq_input_host': '127.0.0.1',
        'zmq_http_host': '127.0.0.1',
        'zmq_data_host': '127.0.0.1',
        # ZMQ messaging ports
        'zmq_input_port': 8022,
        'zmq_http_port': 8081,
        'zmq_data_port': 8082,

        # Timeouts
        'send_stream_timeout': 0.3,
        'send_analytics_timeout': 60,
        'reset_subjs_timeout': 300,
        'filter_trending_timeout': 0.7,
        'render_trending_timeout': 0.3,
        'gc_timeout': 300,

        # fw_eo output from funcions_matching threshold 
        'fo_compare_threshold': 65,
        'so_compare_threshold': 80,
        #svo thresholds
        'subj_compare_threshold': 85,
        'verb_compare_threshold': 0.5,
        'obj_compare_threshold': 0.5,
        # twitch_stream trending params
        'matched_init_base': 50,
        'matched_add_base': 15,
        'matched_add_user_base':500,
        'buffer_mult': 4,
        'decay_msg_base': 1,
        'decay_msg_min_limit': 0.4,
        'decay_time_mtch_base': 4,
        'decay_time_base': 0.2
    },

    # Twitter Stream Config
    'twitter_config': {
        # Attributes
        'self': 'twitter',
        'debug': False,

        # DEV ZMQ hosts
        'zmq_input_host': '127.0.0.1',
        'zmq_http_host': '127.0.0.1',
        'zmq_data_host': '127.0.0.1',
        # ZMQ messaging ports
        'zmq_input_port': 8023,
        'zmq_http_port': 8081,
        'zmq_data_port': 8082,

        # Timeouts
        'send_stream_timeout': 0.7,
        'send_analytics_timeout': 60,
        'reset_subjs_timeout': 300,
        'filter_trending_timeout': 0.7,
        'filter_content_timeout': 5,
        'render_trending_timeout': 0.7,
        'gc_timeout': 300,

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
        'content_max_time': 7200,
        'content_max_size': 20
    },

    # Twitter Stream Config
    'reddit_config': {
        # Attributes
        'self': 'reddit',
        'debug': False,

        # DEV ZMQ hosts
        'zmq_input_host': '127.0.0.1',
        'zmq_http_host': '127.0.0.1',
        'zmq_data_host': '127.0.0.1',
        # ZMQ messaging ports
        'zmq_input_port': 8024,
        'zmq_http_port': 8081,
        'zmq_data_port': 8082,

        'send_stream_timeout': 0.7,
        'send_analytics_timeout': 60,
        'reset_subjs_timeout': 300,
        'filter_trending_timeout': 0.7,
        'filter_content_timeout': 5,
        'render_trending_timeout': 0.7,
        'gc_timeout': 300,

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
        'content_max_time': 7200,
        'content_max_size': 20
    }
}

data_config = {
    # DEV ZMQ hosts
    'zmq_http_data_host': '127.0.0.1',
    'zmq_data_host': '127.0.0.1',
    'zmq_proc_host': '127.0.0.1',


    #Data Server Ports
    'zmq_data_port': 8082,
    'zmq_http_data_port': 8085,
    'zmq_proc_port': 8050,

    #ML clustering
    'num_cluster_procs': 5,
    'hdb_min_cluster_size': 3,
    'subj_pctile': 35
}

server_config = {
    'zmq_server_host': '127.0.0.1',
    'zmq_server_port': 8083,

    # Twitter initialized target streams
    'init_streams': {
        'twitch': ['nalcs1'],
        'twitter': ['trump'],
        'reddit': ['soccer']
    }
}

http_config = {
    'host': '127.0.0.1',
    'port': 80,

    # DEV ZMQ hosts
    'zmq_http_host': '127.0.0.1',
    'zmq_http_data_host': '127.0.0.1',
    'zmq_server_host': '127.0.0.1',
    'zmq_http_port': 8081,
    'zmq_http_data_port': 8085,
    'zmq_server_port': 8083,

    'twitch_monitor_timeout': 15,
    'twitter_monitor_timeout': 15,
    'reddit_monitor_timeout': 15
}
