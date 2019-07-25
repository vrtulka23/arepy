import datetime

def timeStamp(strf="%y%m%d_%H%M"):
    return datetime.datetime.now().strftime(strf)
