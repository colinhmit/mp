import psycopg2

db_str = 'testdb'
host_str = 'currentsdb.clocpkfrofip.us-west-2.rds.amazonaws.com'
port_str = '5432'
user_str = 'currentsdev'
pw_str = 'AndrewColinEben!'

con = psycopg2.connect(dbname = db_str, host=host_str, port=port_str, user=user_str, password=pw_str)
cur = con.cursor()
#cur.execute("CREATE TABLE test_stream (id serial PRIMARY KEY, time double precision, src varchar, stream varchar, username varchar, message varchar);")

#con.commit()
#cur.close()
#con.close()

f = open('/Users/colinh/Repositories/mp/src/logs/skt_rox_g5.txt', 'r')

for line in f:
    str_msg = line.split("_")
    if len(str_msg) == 3:
        cur.execute("INSERT INTO test_stream (time, src, stream, username, message) VALUES (%s, %s, %s, %s, %s)", (str_msg[0],'internal','test',str_msg[1], str_msg[2].decode('utf-8')))

con.commit()

# timekeys = sorted(strmdict.iterkeys())
# ts_start = time.time()
# while (len(timekeys) > 0) & (not self.stop):
#     timekey = timekeys[0]
#     if (time.time() - ts_start) > (timekey-self.timestart):
#         self.Q.put(json.dumps(strmdict[timekey]))
#         timekeys.pop(0)

# #