import json
import os
import re
import yaml
from tqdm import tqdm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

KEYWORDS_FILE = 'keywords.yml'


def loadKeywords():
    with open(KEYWORDS_FILE, 'r') as f:
        keywords = yaml.safe_load(f)

    papKeywords  = keywords['papKeywords']
    oppoKeywords = keywords['oppoKeywords']

    # Add word boundaries
    papKeywords  = [r"\b%s\b" % keyword for keyword in papKeywords]
    oppoKeywords = [r"\b%s\b" % keyword for keyword in oppoKeywords]

    return papKeywords, oppoKeywords


def loadComments(years, months):
    def loadCommentsFile(name):
        with open(name, 'r') as f:
            comments = json.load(f)
        print('Loaded %s' % name)
        return comments

    def loadMonthComment(year, month):
        monthComments = []
        nonPartCommentPath = 'data/comments-%d-%.2d.json' % (year, month)
        if os.path.exists(nonPartCommentPath):
            monthComments += loadCommentsFile(nonPartCommentPath)
        else:
            names = [entry.name for entry in os.scandir('data/') if 'comments-%d-%.2d' % (year, month) in entry.name]
            for part in range(1, len(names) + 1):
                partCommentPath = 'data/comments-%d-%.2d-%d.json' % (year, month, part)
                monthComments += loadCommentsFile(partCommentPath)
        return monthComments

    monthComments = [loadMonthComment(year, month) for year in years for month in months]
    flattenedComments = [cmt for monthCmt in monthComments for cmt in monthCmt]
    print('Loaded %d comments' % len(flattenedComments))
    return flattenedComments


def filterComments(comments, keywordsFor, keywordsAgainst):
    def filterFn(comment, keywords):
        return any([re.search(keyword, comment['body'].lower()) for keyword in keywords])

    filteredComments = []
    for comment in tqdm(comments):
        if filterFn(comment, keywordsFor) and not filterFn(comment, keywordsAgainst):
            filteredComments.append(comment)

    return filteredComments


def getSentiment(comments):
    analyser = SentimentIntensityAnalyzer()
    sentiment = []
    for comment in tqdm(comments):
        score = analyser.polarity_scores(comment['body'])['compound']
        sentiment.append({ 'body': comment['body'], 'author': comment['author'], 'created_utc': comment['created_utc'], 'score': score })
    return sentiment


if __name__ == '__main__':
    comments = loadComments([2018], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    papKeywords, oppoKeywords = loadKeywords()

    # Disregard posts by sneakpeek_bot
    comments = [cmt for cmt in comments if cmt['author'] != 'sneakpeek_bot']

    print('Filtering comments for PAP keywords...')
    papComments  = filterComments(comments, papKeywords, oppoKeywords)
    print('Found %d PAP comments' % len(papComments))

    print('Filtering comments for opposition keywords...')
    oppoComments = filterComments(comments, oppoKeywords, papKeywords)
    print('Found %d opposition comments' % len(oppoComments))

    print('Getting sentiments for PAP comments...')
    papSentiment  = getSentiment(papComments)

    print('Getting sentiments for opposition comments...')
    oppoSentiment = getSentiment(oppoComments)

    with open('data/sentiment-2018-01-12-pap.json', 'w') as f:
        json.dump(papSentiment, f)
    with open('data/sentiment-2018-01-12-oppo.json', 'w') as f:
        json.dump(oppoSentiment, f)
