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
#     cur.execute("DROP TABLE trending;")
# except Exception, e:
#     cur.execute("rollback;")
#     print 'failed dropping trending'

# cur.execute("CREATE TABLE trending (id serial PRIMARY KEY, time timestamp, src varchar, stream varchar, num integer, username varchar, score double precision, message varchar, first_rcv_time timestamp, uuid varchar, src_id varchar);")

# try:
#     cur.execute("DROP TABLE input_chat_stats;")
# except Exception, e:
#     cur.execute("rollback;")
#     print 'failed dropping input_chat_stats'

# cur.execute("CREATE TABLE input_chat_stats (id serial PRIMARY KEY, time timestamp, src varchar, stream varchar, num integer, num_comments integer, num_commenters integer, tot_comments integer, tot_commenters integer);")

# try:
#     cur.execute("DROP TABLE input_view;")
# except Exception, e:
#     cur.execute("rollback;")
#     print 'failed dropping input_view'

# cur.execute("CREATE TABLE input_view (id serial PRIMARY KEY, time timestamp, src varchar, stream varchar, num integer, num_viewers integer);")

# try:
#     cur.execute("DROP TABLE sentiment;")
# except Exception, e:
#     cur.execute("rollback;")
#     print 'failed dropping sentiment'

# cur.execute("CREATE TABLE sentiment (id serial PRIMARY KEY, time timestamp, src varchar, stream varchar, type varchar, num integer, sentiment double precision);")

# try:
#     cur.execute("DROP TABLE subjects;")
# except Exception, e:
#     cur.execute("rollback;")
#     print 'failed dropping subjects'

# cur.execute("CREATE TABLE subjects (id serial PRIMARY KEY, time timestamp, src varchar, stream varchar, num integer, subject varchar, score double precision, sentiment double precision);")

cur.execute("DELETE FROM input_chat WHERE src='twitter'")
cur.execute("DELETE FROM trending WHERE src='twitter'")
cur.execute("DELETE FROM input_chat_stats WHERE src='twitter'")
cur.execute("DELETE FROM input_view WHERE src='twitter'")
cur.execute("DELETE FROM sentiment WHERE src='twitter'")
cur.execute("DELETE FROM subjects WHERE src='twitter'")

cur.execute("DELETE FROM input_chat WHERE stream='shroud'")
cur.execute("DELETE FROM trending WHERE stream='shroud'")
cur.execute("DELETE FROM input_chat_stats WHERE stream='shroud'")
cur.execute("DELETE FROM input_view WHERE stream='shroud'")
cur.execute("DELETE FROM sentiment WHERE stream='shroud'")
cur.execute("DELETE FROM subjects WHERE stream='shroud'")

con.commit()
cur.close()
con.close()