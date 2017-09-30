import psycopg2
import datetime
import random
import time

db_str = 'testdb'
host_str = 'currentsdb.clocpkfrofip.us-west-2.rds.amazonaws.com'
port_str = '5432'
user_str = 'currentsdev'
pw_str = 'AndrewColinEben!'

con = psycopg2.connect(dbname = db_str, host=host_str, port=port_str, user=user_str, password=pw_str)
cur = con.cursor()

src = 'internal'
stream = 'skt_rox'
num = 0

interval = 5

num_viewers = 223405
tot_viewers = 643405

concur_viewers_min = -4000
concur_viewers_max = 7000

tot_viewers_base = 1000

start_time = datetime.datetime.now()
while (datetime.datetime.now()-start_time).total_seconds() < 3900:
    thistime = datetime.datetime.now()
    num_viewers += random.randint(concur_viewers_min,concur_viewers_max)
    tot_viewers += random.randint(0, tot_viewers_base)
    print (thistime.isoformat(),src,stream,num,num_viewers, tot_viewers)
    cur.execute("INSERT INTO view_stats (time, src, stream, num, num_viewers, tot_viewers) VALUES (%s, %s, %s, %s, %s, %s)", (thistime.isoformat(),src,stream,num,num_viewers, tot_viewers))
    con.commit()
    num += 1
    time.sleep(interval-(datetime.datetime.now()-thistime).total_seconds())


#cur.execute("SELECT COUNT(*) FROM input_chat;")
#cur.fetchone()


#cur.execute("SELECT src, stream, COUNT (*) FROM input_chat GROUP BY src, stream;")
