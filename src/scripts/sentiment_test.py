import psycopg2
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

db_str = 'testdb'
host_str = 'currentsdb.clocpkfrofip.us-west-2.rds.amazonaws.com'
port_str = '5432'
user_str = 'currentsdev'
pw_str = 'AndrewColinEben!'

con = psycopg2.connect(dbname = db_str, host=host_str, port=port_str, user=user_str, password=pw_str)
cur = con.cursor()

cur.execute("SELECT * FROM input_chat where src='internal';")
posts = cur.fetchall()
sia = SIA()
pos_list = []
neg_list = []

for post in posts:
    text = post[5].rstrip()
    res = sia.polarity_scores(text)
    # Uncomment the following line to get the polarity results
    # for each post as shown in article's image
    print('////////////////////////')
    print(text)
    print(res)
    if res['compound'] > 0.2:
        pos_list.append(text)
    elif res['compound'] < -0.2:
        neg_list.append(text)


#cur.execute("SELECT src, stream, COUNT (*) FROM input_chat GROUP BY src, stream;")
