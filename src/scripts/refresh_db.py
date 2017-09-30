import psycopg2

db_str = 'testdb'
host_str = 'currentsdb.clocpkfrofip.us-west-2.rds.amazonaws.com'
port_str = '5432'
user_str = 'currentsdev'
pw_str = 'AndrewColinEben!'

con = psycopg2.connect(dbname = db_str, host=host_str, port=port_str, user=user_str, password=pw_str)
cur = con.cursor()

# try:
#     cur.execute("DROP TABLE input_chat;")
# except Exception, e:
#     cur.execute("rollback;")
#     print 'failed dropping input_chat'

# cur.execute("CREATE TABLE input_chat (id serial PRIMARY KEY, time timestamp, src varchar, stream varchar, username varchar, message varchar, uuid varchar, src_id varchar);")

# try:
#     cur.execute("DROP TABLE stream_chat;")
# except Exception, e:
#     cur.execute("rollback;")
#     print 'failed dropping stream_chat'

# cur.execute("CREATE TABLE stream_chat (id serial PRIMARY KEY, time timestamp, src varchar, stream varchar, num integer, username varchar, score double precision, message varchar, first_rcv_time timestamp, uuid varchar, src_id varchar);")

# try:
#     cur.execute("DROP TABLE input_chat_stats;")
# except Exception, e:
#     cur.execute("rollback;")
#     print 'failed dropping input_chat_stats'

# cur.execute("CREATE TABLE input_chat_stats (id serial PRIMARY KEY, time timestamp, src varchar, stream varchar, num integer, num_comments integer, num_commenters integer, tot_comments integer, tot_commenters integer);")

try:
    cur.execute("DROP TABLE view_stats;")
except Exception, e:
    cur.execute("rollback;")
    print 'failed dropping view_stats'

cur.execute("CREATE TABLE view_stats (id serial PRIMARY KEY, time timestamp, src varchar, stream varchar, num integer, num_viewers integer, tot_viewers integer);")


con.commit()
cur.close()
con.close()