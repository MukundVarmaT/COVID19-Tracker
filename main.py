import data
import time
import simulate
import scipy.optimize
from scipy import interpolate
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pickle
import pandas as pd

class covid:
    def __init__(self):
        self.all_data = data.fetch_data()
        self.find_countries()
        self.country_params = {}
        self.get_real_data()  
        self.simulator = simulate.simulate_epidemic(5, 1.9, 2)
        self.colors = {
            "active": "#FFA500",
            "deaths": "#B22222",
            "recovered": "#008000",
        }
    
    def get_lat_long(self):
        self.lat = []
        self.long = []
        lat_long = pd.read_csv("data/lat_long.csv")
        for i in range(len(lat_long)):
            self.lat.append(lat_long["lat"][i])
            self.long.append(lat_long["long"][i])
        
            
    # function to get all the countries    
    def find_countries(self):
        self.countries = [x for x in self.all_data]
        self.countries.remove("MS Zaandam")
        self.countries.remove("Holy See")
        self.countries.remove("Diamond Princess")
    
    # getting real data
    def get_real_data(self):
        self.country_real = {}
        c_remove = []
        for country in self.countries:
            time, cases, deaths, recovered = data.get_data(country, self.all_data)
            if time == []:
                c_remove.append(country)
            else:    
                self.country_real[country] = {"time":time, "cases":cases, "deaths":deaths, "recovered": recovered}
        # remove all the unwanted countries - less data
        for rem in c_remove:
            self.countries.remove(rem)
    
    def remove_fractions(self, time, sick, recovered, deaths):
        t, s, r, d = [], [], [], []
        i = 0
        while i < len(time):
            t.append(time[i])
            s.append(sick[i])
            r.append(recovered[i])
            d.append(deaths[i])
            i = i + 2
        return t, s, r, d        
    
    def simulate_country(self, country, plot=False, extra=0):
        time_ref, cases_ref, deaths_ref, recovered_ref = self.country_real[country].values()
        if country in self.country_params:
            a, b, c = self.country_params[country]
        else:    
            a, b, c = self.simulator.fit_country(time_ref, cases_ref, recovered_ref, deaths_ref)
            self.country_params[country] = (a, b, c)
        time, sick, recovered, deaths = self.simulator.calculate_epidemic(len(time_ref)+extra, 1e5, cases_ref[0], a, b, c)
        time, sick, recovered, deaths = self.remove_fractions(time, sick, recovered, deaths)
        if plot:
            self.plot_all(country, time, sick, recovered, deaths)
        else:
            return time, sick, recovered, deaths
    
    def convert_dates(self, start, num_days):
        
        start = datetime.strptime(start, '%Y-%m-%d').date()
        days = []
        for i in range(num_days):
            day = start + timedelta(days=i)
            days.append(day)
        return days
        
    def plot_all(self, country, time, sick, recovered, deaths):
        time_ref, cases_ref, deaths_ref, recovered_ref = self.country_real[country].values()
        x1 = self.convert_dates(time_ref[0], len(time_ref))
        x2 = self.convert_dates(time_ref[0], len(time))
        
        plt.figure()
        plt.scatter(x1, cases_ref, c = self.colors["active"])
        plt.scatter(x1, recovered_ref, c = self.colors["recovered"])
        plt.scatter(x1, deaths_ref, c = self.colors["deaths"])
        
        plt.plot(x2, sick, c = self.colors["active"])
        plt.plot(x2, recovered, c = self.colors["recovered"])
        plt.plot(x2, deaths, c = self.colors["deaths"])
        
        plt.show()

    def fit_all(self, extra):
        self.all_simulated_data = {}
        for country in self.countries:
            time_ref, _, _, _ = self.country_real[country].values()
            time, sick, _, _ = self.simulate_country(country, False, 60)
            days = self.convert_dates(time_ref[0], len(time))
            self.all_simulated_data[country] = {"days":days, "active":sick}
        with open('data/all_country.pickle', 'wb') as handle:
            pickle.dump(self.all_simulated_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    def load_data(self):
        with open('data/all_country.pickle', 'rb') as handle:
            self.all_simulated_data = pickle.load(handle)
    
    
if __name__ == "__main__":
    start = time.time()
    COVID = covid()
    # COVID.simulate_country("India", True, 60)
    # COVID.fit_all(60)
    print(time.time() - start)