from hostport_config import *

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
    # timing
    'reset_subjs_refresh': 600
}

content_config = {
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

stream_chat_config = {
    # attr
    'src': 'DEFAULT'

    # settings
    'trending': False,
    'content': False,
    'nlp': False,

    # timing
    'send_stream_refresh': 0.3,

    # parsers
    'modules': {
        'internal':     'src.sources.internal._functions_chat',
        'twitch':       'src.sources.twitch._functions_chat',
        'twitter':      'src.sources.twitter._functions_chat',
        'reddit':       'src.sources.reddit._functions_chat'
    },

    # components
    'trending_config': trending_config,
    'content_config': content_config,
    'nlp_config': nlp_config
}
