from tweepy import Stream , OAuthHandler
from tweepy.streaming import StreamListener
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from unidecode import unidecode
import time
import pandas as pd
import threading

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
                # print(len(tweet_list))
                sent_list.append(sentiment) 
            
            if len(tweet_list) == 10:
                temp = pd.DataFrame({"Tweet":tweet_list, "Sentiment":sent_list})
                tweet_csv = tweet_csv.append(temp, ignore_index=True)
                tweet_csv.to_csv("tweets.csv", index=False)
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

if __name__ == "__main__":
    t = threading.Thread(target=stream_tweets)
    t.start()