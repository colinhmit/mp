import psycopg2

db_str = 'testdb'
host_str = 'currentsdb.clocpkfrofip.us-west-2.rds.amazonaws.com'
port_str = '5432'
user_str = 'currentsdev'
pw_str = 'AndrewColinEben!'

con = psycopg2.connect(dbname = db_str, host=host_str, port=port_str, user=user_str, password=pw_str)
cur = con.cursor()

#cur.execute("SELECT COUNT(*) FROM input_chat;")
#cur.fetchone()


#cur.execute("SELECT src, stream, COUNT (*) FROM input_chat GROUP BY src, stream;")
