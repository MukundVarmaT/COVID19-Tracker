import re
import numpy as np
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pd 
import sys
from PIL import Image

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
        background_color='white',
        stopwords=stopwords,
        width=1600,
        height=800,
        random_state=21,
        colormap='jet',
        max_words=50,
        max_font_size=200).generate(all_words)

    plt.axis('off')
    plt.title(name, fontsize=40)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.savefig(name+".png")

def stack_horizontally():
    images = [Image.open(x) for x in ['positive-wordcloud.png', 'negative-wordcloud.png']]
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)
    new_im = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]
    new_im.save('wordcloud.png')  

def data_to_cloud(data):
    for i in range(len(data)):
        data["Tweet"][i] = clean_tweets(data["Tweet"][i])
    tw_pos = data[data['Sentiment'] >= 0]['Tweet']
    word_cloud(tw_pos, "positive-wordcloud")
    tw_neg = data[data['Sentiment'] <= 0]['Tweet']
    word_cloud(tw_neg, "negative-wordcloud")
    stack_horizontally()

if __name__ == "__main__":
    data = pd.read_csv("tweets.csv")
    data_to_cloud(data)
    