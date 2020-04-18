import json
import urllib
import requests
import datetime
import os

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