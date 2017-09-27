from src.config.socket_config import *

##############################################################################
# Chat Input
##############################################################################

chat_conn_config = {
    # attributes
    'src': 'internal',

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_INTERNAL,

    # connection creds
    'host': INTERNAL_HOST,
    'port': INTERNAL_PORT
}

chat_dist_config = {
    # attributes
    'src': 'internal',

    # distributor settings
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_INTERNAL,
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_INTERNAL
}

replay_config = {
    # path
    'logpath': '/Users/colinh/Repositories/mp/src/analytics/logs/',

    # connection
    'host': INTERNAL_HOST,
    'port': INTERNAL_PORT
}

##############################################################################
# Stream
##############################################################################

trending_config = {
    # attributes
    'src': 'internal',

    # matching logic
    'base_svo_match': False
}

enrich_config = {
    # attributes
    'src': 'internal'
}

nlp_config = {
    # attributes
    'src': 'internal'
}

stream_chat_config = {
    # attributes
    'src': 'internal',
    'trending': True,
    'enrich': False,
    'nlp': True,

    # module
    'module': 'src.sources.internal._functions_chat',

    # messaging
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_INTERNAL
}

##############################################################################
# Master
##############################################################################

internal_config = {
    # attributes
    'src': 'internal',

    # api

    # input components
    'chat_conn_config': chat_conn_config,
    'chat_dist_config': chat_dist_config,
    'replay_config': replay_config,

    # stream chat components
    'trending_config': trending_config,
    'enrich_config': enrich_config,
    'nlp_config': nlp_config,
    'stream_chat_config': stream_chat_config
}
