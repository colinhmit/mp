import time

red = "\033[01;31m{0}\033[00m"


def pp(message, mtype='INFO'):
    mtype = mtype.upper()
    if mtype == "ERROR":
        mtype = red.format(mtype)
    print '[%s] [%s] %s' % (time.strftime('%H:%M:%S',
                            time.gmtime()),
                            mtype,
                            message)
