
from spacy.en import English
from datetime import datetime
from nlp_subj import findSVOs

parser = English()


msg = "At this point, Trump's failure to release his taxes is a vital national security issue. We should not pay our taxes until he releases his."

msg2 = "Trump must release his tax forms! His failure so far is unbelievable"

msg = unicode(msg)
msg2 = unicode(msg2)

print "Parsing msg1"
print (datetime.now())
parse1 = parser(msg)
print (datetime.now())

print "Parsing msg2"
print (datetime.now())
parse2 = parser(msg2)
print (datetime.now())

print "SVOS 1"
print (datetime.now())
svos1 = findSVOs(parse1)
print (datetime.now())

print "SVOS 2"
print (datetime.now())
svos2 = findSVOs(parse2)
print (datetime.now())


