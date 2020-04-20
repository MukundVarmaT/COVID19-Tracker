from tweepy import Stream , OAuthHandler
from tweepy.streaming import StreamListener
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from unidecode import unidecode
import time
import pandas as pd
import threading
import re
import numpy as np
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import sys
from PIL import Image

analyzer = SentimentIntensityAnalyzer()
tweet_csv = pd.DataFrame({"Tweet":[], "Sentiment":[]})
tweet_list = []
sent_list = []

access_token = "1063757584379703302-U58clPYTPInOy4T4BAgyLj4fQg13FG"
access_token_secret = "kj0kWYqIxZ1N4NVmuon5VFsEXart8R9aDyZm4BSbFlHYS"
customer_key = "yTtkeOE6wpRqdLffiHRLz8gtJ"
customer_secret = "thQGdqUmOPdQrueIDBSOrIRl71hMAoZA67GedpIfD50X2lrKJj"


class listener(StreamListener):

    def on_data(self, data):
        try:
            global tweet_list, sent_list, tweet_csv
            data = json.loads(data)
            tweet = unidecode(data['text'])
            
            if "corona" in tweet.lower() or "covid" in tweet.lower():
                time_ms = data['timestamp_ms']
                vs = analyzer.polarity_scores(tweet)
                sentiment = vs['compound']
                tweet_list.append(tweet)
                sent_list.append(sentiment) 
            
            if len(tweet_list) == 10:
                temp = pd.DataFrame({"Tweet":tweet_list, "Sentiment":sent_list})
                tweet_csv = tweet_csv.append(temp, ignore_index=True)
                tweet_csv.to_csv("data/tweets.csv", index=False)
                tweet_list = []
                sent_list = []
      
        except KeyError as e:
            pass
        return(True)

    def on_error(self, status):
        print(status)


def stream_tweets():
    while True:
        try:
            auth = OAuthHandler(customer_key, customer_secret)
            auth.set_access_token(access_token, access_token_secret)
            twitterStream = Stream(auth, listener())
            twitterStream.filter(track=["a","e","i","o","u"])
        except Exception as e:
            print(str(e))
            time.sleep(5)

def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)        
    return input_txt
def clean_tweets(lst):
    # remove twitter Return handles (RT @xxx:)
    lst = np.vectorize(remove_pattern)(lst, "RT @[\w]*:")
    # remove twitter handles (@xxx)
    lst = np.vectorize(remove_pattern)(lst, "@[\w]*")
    # remove URL links (httpxxx)
    lst = np.vectorize(remove_pattern)(lst, "https?://[A-Za-z0-9./]*")
    # remove special characters, numbers, punctuations (except for #)
    lst = np.core.defchararray.replace(lst, "[^a-zA-Z#]", " ")
    return lst

def word_cloud(wd_list, name):
    stopwords = set(STOPWORDS)
    all_words = ' '.join([str(text) for text in wd_list])
    wordcloud = WordCloud(
        stopwords=stopwords,
        width=1600,
        height=800,
        random_state=21,
        colormap='jet',
        max_words=50,
        max_font_size=200).generate(all_words)

    plt.axis('off')
    fig = plt.imshow(wordcloud, interpolation="bilinear")
    fig.axes.get_xaxis().set_visible(False)
    fig.axes.get_yaxis().set_visible(False)
    plt.savefig("data/"+name+".png",bbox_inches='tight',pad_inches = 0)

def stack_horizontally():
    images = [Image.open(x) for x in ['data/positive-wordcloud.png', 'data/negative-wordcloud.png']]
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)
    new_im = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]
    new_im.save('data/wordcloud.png')  

def data_to_cloud(data):
    for i in range(len(data)):
        data["Tweet"][i] = clean_tweets(data["Tweet"][i])
    tw_pos = data[data['Sentiment'] >= 0]['Tweet']
    word_cloud(tw_pos, "positive-wordcloud")
    tw_neg = data[data['Sentiment'] <= 0]['Tweet']
    word_cloud(tw_neg, "negative-wordcloud")
    stack_horizontally()

if __name__ == "__main__":
    # t = threading.Thread(target=stream_tweets)
    # t.start()
    data = pd.read_csv("data/tweets.csv")
    data_to_cloud(data)
    