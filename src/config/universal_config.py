INTERNAL_ON = False
TWITCH_ON = False
TWITTER_ON = False
REDDIT_ON = True



#HOSTS & PORTS
#PROD SETTING
local_host = '0.0.0.0'
http_host = '172.31.3.149'
server_host = '172.31.13.182'
internal_host = '172.31.13.182'
http_host = '172.31.13.182'
main_port = 80

#DEV SETTING
# local_host = '0.0.0.0'
# http_host = '0.0.0.0'
# server_host = '0.0.0.0'
# internal_host = '0.0.0.0'
# http_host = '0.0.0.0'
# main_port = 4808



LOCAL_HOST = '0.0.0.0' #/ '0.0.0.0'
INTERNAL_HOST = '0.0.0.0' #/ '172.31.13.182'
INPUT_HOST = '0.0.0.0' #/ '172.31.13.182'
DIST_HOST = '0.0.0.0' #/ '172.31.13.182'
STREAM_HOST = '0.0.0.0' #/ '172.31.13.182'

INTERNAL_PORT = 8000

INPUT_PORT_INTERNAL = 8010
INPUT_PORT_TWITCH = 8011
INPUT_PORT_TWITTER = 8012
INPUT_PORT_REDDIT = 8013

DIST_PORT_INTERNAL = 8020
DIST_PORT_TWITCH = 8021
DIST_PORT_TWITTER = 8022
DIST_PORT_REDDIT = 8023

STREAM_PORT_INTERNAL = 8030
STREAM_PORT_TWITCH = 8031
STREAM_PORT_TWITTER = 8032
STREAM_PORT_REDDIT = 8033

# internal_port = 8000
# http_port = 8001

# irc_input_port = 8002
# irc_proc_port = 8012
# irc_stream_port = 8022

# twtr_input_port = 8003
# twtr_proc_port = 8013
# twtr_stream_port = 8023

# rddt_input_port = 8004
# rddt_proc_port = 8014
# rddt_stream_port = 8024

# internal_input_port = 8005

# http_input_port = 8006



# ntv_proc_port = 8015
# ntv_stream_port = 8025

# http_port = 8081
# http_data_port = 8085
# data_port = 8082
# data_proc_port = 8050
# server_port = 8083

# http_config = {
#     # attributes
#     'self': 'http',

#     # messaging
#     'http_port': http_port,
#     'input_host': local_host,
#     'input_port': http_input_port,
    
#     # prod log path
#     #'log_path': '/home/ec2-user/mp/src/logs/'
#     # dev log path
#     'log_path': '/Users/colinh/Repositories/mp/src/logs/'
# }

##############################################################################
# Input
##############################################################################

internal_config = {
    # attributes
    'self': 'internal',

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_INTERNAL,
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_INTERNAL,
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_INTERNAL,

    # prod creds
    'host': INTERNAL_HOST,
    'port': INTERNAL_PORT
}

twitch_config = {
    # attributes
    'self': 'twitch',
    'socket_buffer_size': 4096,

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_TWITCH,
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_TWITCH,
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_TWITCH,

    # prod creds   
    'server': 'irc.twitch.tv',
    'port': 6667,
    'username': 'chrendin',
    'client_id': 'r4jy4y7lwnzoez92z29zlgjlqggdyz',
    'oauth_password': 'oauth:1a6qgh8wz0b0lb2ue5zenht2lrkcdx'
}

twitter_config = {
    # attributes
    'self': 'twitter',

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_TWITTER,
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_TWITTER,
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_TWITTER,

    # prod creds
    # 'consumer_token': 'b4pRX7KQPnNQpdyOrC4FTT9Wn',
    # 'consumer_secret': 'GYgrnWSQYzRhD2rCHCXkLLba2bTa0qQ7OCqOGCRB3XShEc4f2d',
    # 'access_token': '784870359241809920-pSQiIXkQXn8miVsqnL6LQrOfzTY7Tix',
    # 'access_secret': 'Olqq3CSWZ5ozLSqRubTIl3AgsCg27tkbfTGLhYAr4lXpd'
                    
    # dev creds #1
    # 'consumer_token': 'lTImlMFo1GZzqJ5dynMHoOkEK',
    # 'consumer_secret': 'hkAYOdEN1nqmTtJBszgrC5VZE7gSFtN2nqgFsHxZbl8v8QVR0G',
    # 'access_token': '805548030816645120-aNstjukeFNVparl3x8lb8dyfUgIQzbf',
    # 'access_secret': 'QHpVzvSBDPTlQrY4k65ip0k3JFrQRIfKHv8JLUM43QTQw'

    # dev creds #2
    # 'consumer_token': 'brULNlsL5AI80FsiMAeH3us42',
    # 'consumer_secret': 'kdPYjOkOIR8NqnXqr7MZvTlR4mPwdMwF80KTytaeHUKFmNCCu5',
    # 'access_token': '178112532-kQ62pLaDjRrPEEn3W7zqsI0tLJgDPMkZgzR0U5iG',
    # 'access_secret': 'eik2jjyu0kLhkr2xNz53182Xa7ayktE646R7XrwQSGuCt'

    # dev creds #3
    'consumer_token': 'cPOClxrPAOdQhgfQfLdcXZL4D',
    'consumer_secret': 'uGByGCcB91FlNizE5edHPuVVmXInXcPIcHKE68n6drh6Achlaq',
    'access_token': '815322092627333121-W3OnWqcm8Mh4SGWJJc7OnmChwWump9m',
    'access_secret': 'MOMWd6pXkqlKxQQuSosa2fKK4sXqx58w2MhgA9G7OWGUq'
}

reddit_config = {
    # attributes
    'self': 'reddit',

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_REDDIT,
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_REDDIT,
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_REDDIT,

    # prod creds
    'client_token': 'bx_HkZiUhuYJCw',
    'client_secret': '5l9swqgf2tAY2je0i61pNklgOCg',
    'user_agent': 'ISS:staycurrents.com:v0.1.9 (by /u/staycurrents)'
}

worker_config = {
    # messaging
    'input_host': INPUT_HOST,
    'input_ports': [INPUT_PORT_INTERNAL, INPUT_PORT_TWITCH,
                    INPUT_PORT_TWITTER, INPUT_PORT_REDDIT],

    'dist_host': DIST_HOST,
    'dist_port_internal': DIST_PORT_INTERNAL,
    'dist_port_twitch': DIST_PORT_TWITCH,
    'dist_port_twitter': DIST_PORT_TWITTER,
    'dist_port_reddit': DIST_PORT_REDDIT,
}

input_config = {
    'internal_on': INTERNAL_ON,
    'twitch_on': TWITCH_ON,
    'twitter_on': TWITTER_ON,
    'reddit_on': REDDIT_ON,


    'num_workers': 30,
    'worker_config': worker_config,

    'internal_config': internal_config,
    'twitch_config': twitch_config,
    'twitter_config': twitter_config,
    'reddit_config': reddit_config
}

##############################################################################

##############################################################################
# Stream
##############################################################################







# stream_config = {
#     # DEV ZMQ hosts/port
#     'zmq_http_host': http_host,
#     'zmq_http_port': http_port,

#     'twitch_featured':{
#         'self': 'twitch',
#         'twitch_client_id': 'r4jy4y7lwnzoez92z29zlgjlqggdyz',
#         'num_featured': 12,
#         'refresh_featured_timeout': 1200
#     },
    
#     'twitter_featured':{
#         'self': 'twitter',
#         'num_featured': 12,
#         'featured_buffer_maxlen': 100,
#         'refresh_featured_timeout': 1200
#     },

#     'reddit_featured':{
#         'self': 'reddit',
#         'refresh_featured_timeout': 1200
#     },

#     'native_featured':{
#         'self': 'native',
#         'refresh_featured_timeout': 1200
#     },

#     'google_sheets':{
#         #AWS Google API Key
#         'sheets_key': '/home/ec2-user/mp/src/config/chrendin_sheets_key.json',
#         #DEV Google API Key
#         #'sheets_key': '/Users/colinh/Repositories/mp/src/config/chrendin_sheets_key.json',
#         'scopes': ['https://www.googleapis.com/auth/spreadsheets.readonly'],
#         'spreadsheetID': '1lz4g3-WvT8EjVc2hogalhnGQmkMb1d1fIvatpLUsano',
#         #PROD Ranges
#         #'featured_data_range': 'Twitter Featured!A2:E',
#         #'featured_live_range': 'Twitter Featured!G2',
#         #Dev Ranges
#         'featured_data_range': 'Dev Twitter Featured!A2:H',
#         'featured_live_range': 'Dev Twitter Featured!J2',
#         'ad_data_range': 'Demo Ad Interface!A2:E',
#         'ad_live_range': 'Demo Ad Interface!J2'
#     },

#     # Twitch Stream Config
#     'twitch_config': {
#         # Attributes
#         'self': 'twitch',
#         'debug': False,

#         # DEV ZMQ hosts
#         'zmq_input_host': local_host,
#         'zmq_http_host': http_host,
#         'zmq_data_host': local_host,
#         # ZMQ messaging ports
#         'zmq_input_port': irc_stream_port,
#         'zmq_http_port': http_port,
#         'zmq_data_port': data_port,

#         # Timeouts
#         'send_stream_timeout': 0.3,
#         'send_analytics_timeout': 60,
#         'reset_subjs_timeout': 600,
#         'filter_trending_timeout': 0.7,
#         'render_trending_timeout': 0.3,
#         'enrich_trending_timeout': 1.0,
#         'enrich_timer': False,

#         # fw_eo output from funcions_matching threshold 
#         'fo_compare_threshold': 65,
#         'so_compare_threshold': 80,
#         #svo thresholds
#         'subj_compare_threshold': 85,
#         'verb_compare_threshold': 0.5,
#         'obj_compare_threshold': 0.5,
#         #enrich params
#         'enrich_base': 50,
#         'enrich_min_len': 5,
#         'last_rcv_enrich_timeout': 5,
#         'last_enrch_enrich_timeout': 45,
#         # twitch_stream trending params
#         'matched_init_base': 50,
#         'matched_add_base': 15,
#         'matched_add_user_base':500,
#         'buffer_mult': 4,
#         'decay_msg_base': 1,
#         'decay_msg_min_limit': 0.4,
#         'decay_time_mtch_base': 4,
#         'decay_time_base': 0.2
#     },

#     # Twitter Stream Config
#     'twitter_config': {
#         # Attributes
#         'self': 'twitter',
#         'debug': False,

#         # DEV ZMQ hosts
#         'zmq_input_host': local_host,
#         'zmq_http_host': http_host,
#         'zmq_data_host': local_host,
#         # ZMQ messaging ports
#         'zmq_input_port': twtr_stream_port,
#         'zmq_http_port': http_port,
#         'zmq_data_port': data_port,

#         # Timeouts
#         'send_stream_timeout': 0.7,
#         'send_analytics_timeout': 60,
#         'reset_subjs_timeout': 600,
#         'filter_trending_timeout': 0.7,
#         'filter_content_timeout': 5,
#         'render_trending_timeout': 0.7,
#         'enrich_trending_timeout': 1.0,
#         'enrich_timer': False,

#         #fw_eo output from funcions_matching threshold 
#         'fo_compare_threshold': 65,
#         'so_compare_threshold': 80,
#         #svo thresholds
#         'subj_compare_threshold': 85,
#         'verb_compare_threshold': 0.3,
#         'obj_compare_threshold': 0.5,
#         #enrich params
#         'enrich_base': 50,
#         'enrich_min_len': 5,
#         'last_rcv_enrich_timeout': 5,
#         'last_enrch_enrich_timeout': 45,
#         #twitter trending params
#         'matched_init_base': 50,
#         'matched_add_base': 15,
#         'matched_add_user_base': 500,     
#         'buffer_mult': 4,
#         'decay_msg_base': 1,
#         'decay_msg_min_limit': 0.4,
#         'decay_time_mtch_base': 4,
#         'decay_time_base': 0.2,

#         #twitter content cutoff
#         'content_max_time': 7200,
#         'content_max_size': 20
#     },

#     # Twitter Stream Config
#     'reddit_config': {
#         # Attributes
#         'self': 'reddit',
#         'debug': False,

#         # DEV ZMQ hosts
#         'zmq_input_host': local_host,
#         'zmq_http_host': http_host,
#         'zmq_data_host': local_host,
#         # ZMQ messaging ports
#         'zmq_input_port': rddt_stream_port,
#         'zmq_http_port': http_port,
#         'zmq_data_port': data_port,

#         'send_stream_timeout': 0.7,
#         'send_analytics_timeout': 60,
#         'reset_subjs_timeout': 600,
#         'filter_trending_timeout': 0.7,
#         'filter_content_timeout': 5,
#         'render_trending_timeout': 0.7,
#         'enrich_trending_timeout': 1.0,
#         'enrich_timer': False,

#         #fw_eo output from funcions_matching threshold 
#         'fo_compare_threshold': 65,
#         'so_compare_threshold': 80,
#         #svo thresholds
#         'subj_compare_threshold': 85,
#         'verb_compare_threshold': 0.3,
#         'obj_compare_threshold': 0.5,
#         #enrich params
#         'enrich_base': 50,
#         'enrich_min_len': 5,
#         'last_rcv_enrich_timeout': 5,
#         'last_enrch_enrich_timeout': 45,
#         #twitter trending params
#         'matched_init_base': 50,
#         'matched_add_base': 15,
#         'matched_add_user_base': 500,     
#         'buffer_mult': 4,
#         'decay_msg_base': 1,
#         'decay_msg_min_limit': 0.4,
#         'decay_time_mtch_base': 4,
#         'decay_time_base': 0.2,

#         #twitter content cutoff
#         'content_max_time': 7200,
#         'content_max_size': 20
#     },

#     # Native Stream Config
#     'native_config': {
#         # Attributes
#         'self': 'native',
#         'debug': False,

#         # DEV ZMQ hosts
#         'zmq_input_host': local_host,
#         'zmq_http_host': http_host,
#         'zmq_data_host': local_host,
#         # ZMQ messaging ports
#         'zmq_input_port': ntv_stream_port,
#         'zmq_http_port': http_port,
#         'zmq_data_port': data_port,

#         'send_stream_timeout': 0.05,
#         'send_analytics_timeout': 60,
#         'reset_subjs_timeout': 600,
#         'filter_trending_timeout': 0.7,
#         'filter_content_timeout': 5,
#         'render_trending_timeout': 0.05,
#         'enrich_trending_timeout': 1.0,
#         'enrich_timer': False,

#         'set_nlp_match_timeout': 5,
#         'nlp_match_threshold': 3,

#         #fw_eo output from funcions_matching threshold 
#         'fo_compare_threshold': 65,
#         'so_compare_threshold': 80,
#         #svo thresholds
#         'subj_compare_threshold': 85,
#         'verb_compare_threshold': 0.3,
#         'obj_compare_threshold': 0.5,
#         #enrich params
#         'enrich_base': 50,
#         'enrich_min_len': 5,
#         'last_rcv_enrich_timeout': 5,
#         'last_enrch_enrich_timeout': 45,
#         #ad params
#         'ad_timeout_base': 180,
#         'ad_loop_timeout': 5,
#         #twitter trending params
#         'matched_init_base': 50,
#         'matched_add_base': 15,
#         'matched_add_user_base': 500,     
#         'buffer_mult': 4,
#         'decay_msg_base': 1,
#         'decay_msg_min_limit': 0.4,
#         'decay_time_mtch_base': 4,
#         'decay_time_base': 0.2
#     }
# }

# data_config = {
#     # DEV ZMQ hosts
#     'zmq_http_data_host': http_host,
#     'zmq_data_host': local_host,
#     'zmq_proc_host': local_host,

#     #Data Server Ports
#     'zmq_data_port': data_port,
#     'zmq_http_data_port': http_data_port,
#     'zmq_proc_port': data_proc_port,

#     #ML clustering
#     'num_cluster_procs': 5,
#     'hdb_min_cluster_size': 3,
#     'subj_pctile': 35
# }

# server_config = {
#     'zmq_server_host': local_host,
#     'zmq_server_port': server_port,

#     # Twitter initialized target streams
#     'init_streams': {
#         'twitch': ['nalcs1'],
#         'twitter': ['trump'],
#         'reddit': ['soccer']
#     }
# }

# ad_config = {
#     'self': 'advertisement',
#     'debug': False,

#     'zmq_http_host': http_host,
#     'zmq_http_port': http_port,
#     'timeout': 120,

#      'google_sheets':{
#         #AWS Google API Key
#         'sheets_key': '/home/ec2-user/mp/src/config/chrendin_sheets_key.json',
#         #DEV Google API Key
#         #'sheets_key': '/Users/colinh/Repositories/mp/src/config/chrendin_sheets_key.json',
#         'scopes': ['https://www.googleapis.com/auth/spreadsheets.readonly'],
#         'spreadsheetID': '1lz4g3-WvT8EjVc2hogalhnGQmkMb1d1fIvatpLUsano',
#         #PROD Ranges
#         #'featured_data_range': 'Twitter Featured!A2:E',
#         #'featured_live_range': 'Twitter Featured!G2',
#         #Dev Ranges
#         'featured_data_range': 'Dev Twitter Featured!A2:H',
#         'featured_live_range': 'Dev Twitter Featured!J2',
#         'ad_data_range': 'Demo Ad Interface!A2:E',
#         'ad_live_range': 'Demo Ad Interface!J2'
#     }
# }

# http_config = {
#     'host': local_host,
#     'port': main_port,

#     # DEV ZMQ hosts
#     'zmq_http_host': local_host,
#     'zmq_http_data_host': local_host,
#     'zmq_server_host': server_host,
#     'zmq_http_port': http_port,
#     'zmq_http_data_port': http_data_port,
#     'zmq_server_port': server_port,

#     'twitch_monitor_timeout': 15,
#     'twitter_monitor_timeout': 15,
#     'reddit_monitor_timeout': 15,

#     'enrich_base': 7
# }