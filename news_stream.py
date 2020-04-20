import requests
from bs4 import BeautifulSoup
import pandas as pd


class news:
    def __init__(self, no_pages):
        self.headlines = []
        self.references = []
        self.description = []
        self.dates = []
        self.no_pages = no_pages
        self.scrap_news()
        self.news_csv = pd.DataFrame()
        self.news_csv["Date"] = self.dates
        self.news_csv["Headlines"] = self.headlines
        self.news_csv["Description"] = self.description
        
    def scrap_news(self):
        for i in range(1, self.no_pages):
            if i == 1:
                URL = 'https://visualizenow.org/corona-news'
            else:
                URL = 'https://visualizenow.org/corona-news' + "?page={}".format(i)
            page = requests.get(URL)

            soup = BeautifulSoup(page.content, 'html.parser')
            a_tag = soup.find_all("a", href=True)
            p_tag = soup.find_all("p")

            for a in a_tag:
                if a.text:
                    h = a.text
                    if len(h.split(" ")) > 3:
                        h = h.replace("\n",  "")
                        h = h.strip()
                        if ".co" in h:
                            self.references.append(h)
                        else:
                            self.headlines.append(h)
        
            for p in p_tag:
                if p.text:
                    c = p.text
                    c = c.replace("\n",  "")
                    c = c.strip()
                    if "..." in c:
                        self.description.append(c)
                    elif "Published" in c:
                        c = c.replace("Published on", "")
                        self.dates.append(c)
                        if len(self.dates)!=len(self.description):
                            self.description.append("N.A")
             
if __name__ == "__main__":
    NEWS = news(5)
