import psycopg2

db_str = 'testdb'
host_str = 'currentsdb.clocpkfrofip.us-west-2.rds.amazonaws.com'
port_str = '5432'
user_str = 'currentsdev'
pw_str = 'AndrewColinEben!'

con = psycopg2.connect(dbname = db_str, host=host_str, port=port_str, user=user_str, password=pw_str)
cur = con.cursor()
cur.execute("CREATE TABLE test (id serial PRIMARY KEY, src varchar, stream varchar, message varchar, src_id varchar);")

con.commit()
cur.close()
con.close()

#cur.execute("INSERT INTO test (src, stream, message, src_id) VALUES (%s, %s, %s, %s)",('native', 'test', 'Hi it's colin', '1234'))