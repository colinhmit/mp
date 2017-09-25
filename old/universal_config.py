

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