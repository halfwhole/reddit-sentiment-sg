# Sentiment analysis tools
# - Google Cloud: https://cloud.google.com/natural-language
# - Pattern: https://github.com/clips/pattern
# - Transformers/TextClassificationPipeline: https://huggingface.co/transformers/main_classes/pipelines.html#textclassificationpipeline

# Original: https://medium.com/@RareLoot/using-pushshifts-api-to-extract-reddit-submissions-fb517b286563
import requests
import json
import csv
import time
import pickle
from datetime import date, datetime

def getPushshiftComments(after, before, sub, query):
    url = 'https://api.pushshift.io/reddit/search/comment/?'
    url += 'size=500&after=' + str(after) + '&before=' + str(before) + '&subreddit=' + str(sub)
    if query: url += 'q=%"' + str(query) + '"'
    while True:
        try:
            r = requests.get(url)
            if r.status_code != 200:
                raise Exception('Status code is %d ' % r.status_code)
            break
        except Exception as e:
            print('Failed, trying again. Error message: %s' % e)
    data = json.loads(r.text)
    return data['data']

def getAllComments(start, end, sub, query):
    after = int(start.timestamp())
    before = int(end.timestamp())
    allComments = []
    while True:
        comments = getPushshiftComments(after, before, sub, query)
        if len(comments) == 0: break
        after = comments[-1]['created_utc']
        print('%d comments up till %s' % (len(comments), datetime.fromtimestamp(after)))
        allComments += comments
    return allComments

def getAllMonthComments(year, month, sub, query):
    start = datetime(year, month, 1, 0, 0, 0, 0)
    end = datetime((year + 1) if month == 12 else year, (month % 12 + 1), 1, 0, 0, 0, 0)
    return getAllComments(start, end, sub, query)

def saveComments(comments, name):
    with open(name, 'w') as f:
        json.dump(comments, f)

def loadComments(name):
    with open(name, 'r') as f:
        comments = json.load(f)
    return comments

def getSaveAllMonthComments(year, month, sub='singapore', query=None):
    filename = 'comments-%d-%.2d.json' % (year, month)
    print('will be saved to %s' % filename)
    monthComments = getAllMonthComments(year, month, sub, query)
    saveComments(monthComments, filename)
    print('saved to %s' % filename)


if __name__ == '__main__':
    # for year in [2018, 2019]:
    #     for month in range(1, 13):
    #         getSaveAllMonthComments(year, month)
    pass
