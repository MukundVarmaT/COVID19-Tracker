import json
import urllib
import requests
import datetime
import os
import time

def days_between(d1, d2):
    d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


def fetch_data():
    url = "https://pomber.github.io/covid19/timeseries.json"
    data = json.loads(requests.get(url).text)
    return data

def get_data(country, data):
    time, cases, deaths, recovered = [], [], [], []
    for entry in data[country]:
        if float(entry["confirmed"]) > 50 and entry["recovered"] is not None:
            time.append(entry["date"])
            recovered.append(float(entry["recovered"]))
            cases.append(float(entry["confirmed"])- float(entry["recovered"]) - float(entry["deaths"]))
            deaths.append(float(entry["deaths"]))
    return time, cases, deaths, recovered

def fetch_india():
    url = "https://api.rootnet.in/covid19-in/stats/history"
    data = json.loads(requests.get(url).text)
    return data

def get_india():
    data = fetch_india()
    data = data["data"]
    indian_data = {}
    for entry in data:
        for i in entry["regional"]:
            c = i["loc"]
            c = c.replace("#","")
            if c not in indian_data:
                indian_data[c] = {"dates":[], "active":[], "dead":[], "recovered":[]}
            indian_data[c]["active"].append(i["totalConfirmed"] - i["discharged"] - i["deaths"])
            indian_data[c]["recovered"].append(i["discharged"])
            indian_data[c]["dead"].append(i["deaths"])
            indian_data[c]["dates"].append(entry["day"])
    return indian_data

if __name__ == "__main__":
    start = time.time()
    indian_data = get_india()
    print(time.time() - start)