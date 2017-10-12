from src.config.socket_config import *

##############################################################################
# Chat Input
##############################################################################

chat_conn_config = {
    # attributes
    'src': 'twitter',

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_TWITTER
}

chat_dist_config = {
    # attributes
    'src': 'twitter',

    # distributor settings
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_TWITTER,
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_TWITTER
}

##############################################################################
# Stream
##############################################################################

trending_config = {
    # attributes
    'src': 'twitter',

    # thread timings
    'render_trending_refresh': 0.7
}

nlp_config = {
    # attributes
    'src': 'twitter'
}

stream_chat_config = {
    # attributes
    'src': 'twitter',
    'trending': True,
    'nlp': True,

    # timing
    'send_trending_refresh': 0.7,

    # module
    'module': 'src.sources.twitter._functions_chat',

    # messaging
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_TWITTER
}

##############################################################################
# Master
##############################################################################

twitter_config = {
    # attributes
    'src': 'twitter',

    # api
    # prod creds
    # 'consumer_token': 'b4pRX7KQPnNQpdyOrC4FTT9Wn',
    # 'consumer_secret': 'GYgrnWSQYzRhD2rCHCXkLLba2bTa0qQ7OCqOGCRB3XShEc4f2d',
    # 'access_token': '784870359241809920-pSQiIXkQXn8miVsqnL6LQrOfzTY7Tix',
    # 'access_secret': 'Olqq3CSWZ5ozLSqRubTIl3AgsCg27tkbfTGLhYAr4lXpd',
                    
    # dev creds #1
    # 'consumer_token': 'lTImlMFo1GZzqJ5dynMHoOkEK',
    # 'consumer_secret': 'hkAYOdEN1nqmTtJBszgrC5VZE7gSFtN2nqgFsHxZbl8v8QVR0G',
    # 'access_token': '805548030816645120-aNstjukeFNVparl3x8lb8dyfUgIQzbf',
    # 'access_secret': 'QHpVzvSBDPTlQrY4k65ip0k3JFrQRIfKHv8JLUM43QTQw'

    # dev creds #2
    # 'consumer_token': 'brULNlsL5AI80FsiMAeH3us42',
    # 'consumer_secret': 'kdPYjOkOIR8NqnXqr7MZvTlR4mPwdMwF80KTytaeHUKFmNCCu5',
    # 'access_token': '178112532-kQ62pLaDjRrPEEn3W7zqsI0tLJgDPMkZgzR0U5iG',
    # 'access_secret': 'eik2jjyu0kLhkr2xNz53182Xa7ayktE646R7XrwQSGuCt',

    # dev creds #3
    'consumer_token': 'cPOClxrPAOdQhgfQfLdcXZL4D',
    'consumer_secret': 'uGByGCcB91FlNizE5edHPuVVmXInXcPIcHKE68n6drh6Achlaq',
    'access_token': '815322092627333121-W3OnWqcm8Mh4SGWJJc7OnmChwWump9m',
    'access_secret': 'MOMWd6pXkqlKxQQuSosa2fKK4sXqx58w2MhgA9G7OWGUq',

    # input components
    'chat_conn_config': chat_conn_config,
    'chat_dist_config': chat_dist_config,

    # stream chat components
    'trending_config': trending_config,
    'nlp_config': nlp_config,
    'stream_chat_config': stream_chat_config
}
