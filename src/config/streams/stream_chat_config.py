from src.config.socket_config import *

##############################################################################
# Components
##############################################################################

trending_config = {
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

nlp_config = {
    # nlp size
    'render_nlp_limit': 5,

    # thread timing
    'render_nlp_refresh': 5,

    #algo params
    'init_base': 11,
    'add_base': 11,
    'decay_perc': 0.98,
    'decay_base': 0.1
}

##############################################################################
# Master
##############################################################################

stream_chat_config = {
    # attr
    'src': 'DEFAULT',

    # db connect
    'db_str': 'testdb',
    'host_str': 'currentsdb.clocpkfrofip.us-west-2.rds.amazonaws.com',
    'port_str': '5432',
    'user_str': 'currentsdev',
    'pw_str': 'AndrewColinEben!',

    # settings
    'trending': False,
    'enrich': False,
    'nlp': False,

    # timing
    'send_trending_refresh': 0.3,
    'send_nlp_refresh': 5.0,
    'db_connect_timeout': 2.0,

    # messaging
    'fwd_host': FWD_HOST,
    'fwd_port': FWD_PORT_INPUT,

    # components
    'trending_config': trending_config,
    'nlp_config': nlp_config
}
