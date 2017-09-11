from hostport_config import *

##############################################################################
# Inputs
##############################################################################

internal_config = {
    # attributes
    'src': 'internal',

    # messaging
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_INTERNAL,

    # prod creds
    'host': INTERNAL_HOST,
    'port': INTERNAL_PORT
}

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


twitch_config = {
    # attributes
    'src': 'twitch',
    'socket_buffer_size': 4096,

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_TWITCH,

    # distributor settings
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
    'src': 'twitter',

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_TWITTER,

    # distributor settings
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
    'src': 'reddit',

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_REDDIT,

    # distributor settings
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_REDDIT,
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_REDDIT,

    # prod creds
    'client_token': 'bx_HkZiUhuYJCw',
    'client_secret': '5l9swqgf2tAY2je0i61pNklgOCg',
    'user_agent': 'ISS:staycurrents.com:v0.1.9 (by /u/staycurrents)'
}

##############################################################################
# Components
##############################################################################

consolidator_config = {
    # matching logic
    'base_svo_match': True,
    'string_match': True,
    'ignore_user': False,
    'dynamic_svo_match': False,
    'svo_match_threshold': 3,

    # fw_eo output from functions_matching threshold 
    'fo_compare_threshold': 65,
    'so_compare_threshold': 80,

    # svo matching thresholds
    'subj_compare_threshold': 85,
    'verb_compare_threshold': 0.5,
    'obj_compare_threshold': 0.5,

    # thread timings
    'filter_trending_refresh': 0.7,
    'render_trending_refresh': 0.3,
    'set_svo_match_refresh': 5,

    # algo params
    'matched_init_base': 50,
    'matched_add_base': 15,
    'matched_add_user_base':500,
    'buffer_mult': 4,
    'decay_msg_base': 1,
    'decay_msg_min_limit': 0.4,
    'decay_time_mtch_base': 4,
    'decay_time_base': 0.2
}

enricher_config = {
    # advertising
    'ad_trigger': False,
    'ad_timer': 180,
    'ad_refresh': 5,

    # timing
    'enrich_timer': False,
    'decay_oldest': False,
    'enrich_refresh': 1.0,
    'last_rcv_enrich_timer': 5,
    'last_enrch_enrich_timer': 45,

    #length
    'enrich_min_len': 5
}

analyzer_config = {
    # timing
    'reset_subjs_refresh': 600
}

aggregator_config = {
    # matching
    'fo_compare_threshold': 65,

    # timing
    'filter_content_refresh': 5,

    # length
    'content_max_time': 7200,
    'content_max_size': 20
}

##############################################################################
# Master
##############################################################################

stream_config = {
    

    'consolidator_config': consolidator_config,
    'enricher_config': enricher_config,
    'analyzer_config': analyzer_config,
    'aggregator_config': aggregator_config
}
