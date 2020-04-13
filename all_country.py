import data
import pandas as pd
import main
import pickle
from datetime import datetime, timedelta

def fit_all():
    map_data = pd.read_csv("map_data.csv")
    cases_country = {}
    min_start = ""
    max_len = 0
    
    temp = data.fetch_data()
    coun = [i for i in temp]
    
    for i in range(len(map_data)):
        
        if map_data["country"][i] not in coun:
            cases_country[map_data["iso_alpha"][i]] = [0]
            continue
        time_sim, cases_sim, healthy_sim, recovered_sim, deaths_sim, start = main.fit_country(map_data["country"][i], 60, start_date=True)
        if time_sim == None:
            cases_country[map_data["iso_alpha"][i]] = [0]
        else:
            j = 0
            c = []
            while j<len(cases_sim):
                c.append(cases_sim[j])
                j = j + 2
            cases_country[map_data["iso_alpha"][i]] = c
            if len(c) > max_len:
                min_start = start
                max_len = len(c)
    
    for i in cases_country:
        if len(cases_country[i]) < max_len:
            cases_country[i] = [0]*(max_len - len(cases_country[i])) + cases_country[i]
    
    return cases_country, min_start, max_len
        
    
    
def load_data():
    with open('cases_country.pickle', 'rb') as handle:
        cases_country = pickle.load(handle)
    with open('days.pickle', 'rb') as handle:
        days = pickle.load(handle)
    return cases_country, days
    
if __name__ == "__main__":
    
    cases_country, start, max_len = fit_all()
    with open('cases_country.pickle', 'wb') as handle:
        pickle.dump(cases_country, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    start = datetime.strptime(start,'%Y-%m-%d').date()
    days = []
    for i in range(max_len):
        day = start+ timedelta(days=i)
        days.append(day)
    
    with open('days.pickle', 'wb') as handle:
        pickle.dump(days, handle, protocol=pickle.HIGHEST_PROTOCOL)  
    
    