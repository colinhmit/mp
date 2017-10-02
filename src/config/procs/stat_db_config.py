##############################################################################
# Chat Velocity
##############################################################################

chat_velocity_config = {
    # db connect
    'db_str': 'testdb',
    'host_str': 'currentsdb.clocpkfrofip.us-west-2.rds.amazonaws.com',
    'port_str': '5432',
    'user_str': 'currentsdev',
    'pw_str': 'AndrewColinEben!',

    #settings
    'interval': 5,
    'lookback': 60
}

##############################################################################
# INPUT CHAT Worker
##############################################################################

chat_sentiment_config = {
    # db connect
    'db_str': 'testdb',
    'host_str': 'currentsdb.clocpkfrofip.us-west-2.rds.amazonaws.com',
    'port_str': '5432',
    'user_str': 'currentsdev',
    'pw_str': 'AndrewColinEben!',

    #settings
    'interval': 5,
    'lookback': 5
}


##############################################################################
# Server
##############################################################################

stat_db_config = {
    # worker setup
    'chat_velocity_config': chat_velocity_config,
    'chat_sentiment_config': chat_sentiment_config
}