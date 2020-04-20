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
        self.state_params = {}
        self.get_real_data()  
        self.simulator = simulate.simulate_epidemic(5, 1.9, 2)
        self.state_simulator = simulate.simulate_epidemic(6.5, 0.9, 1.6)
        self.colors = {
            "active": "#FFA500",
            "deaths": "#B22222",
            "recovered": "#008000",
        }
        self.get_india_data()
    
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
    
    def get_stats(self):
        active = []
        deaths = []
        recovered = []
        for i in self.country_real:
            time_ref, cases_ref, deaths_ref, recovered_ref = self.country_real[i].values()
            active.append(cases_ref[-1])
            deaths.append(deaths_ref[-1])
            recovered.append(recovered_ref[-1])
        return active, deaths, recovered
    
    def select_states(self):
        self.selected_indian_states = []
        self.selected_indian_data = {}
        for state in self.indian_data:
            dates, active, dead, rec = self.indian_data[state].values()
            if max(active) < 50:
                pass
            else:
                d, a, de, r = [], [], [], []
                for i in range(len(active)):
                    if active[i] > 10:
                        d.append(dates[i])
                        a.append(active[i])
                        de.append(dead[i])
                        r.append(rec[i])
                if len(d) > 5:
                    self.selected_indian_states.append(state)
                    self.selected_indian_data[state] = {"dates":d, "active":a, "dead":de, "recovered":r}
                    
    def get_india_data(self):
        self.indian_data = data.get_india()
        self.indian_states = self.indian_data.keys()
        indian_lat_long = pd.read_csv("data/india_lat_long.csv")
        self.indian_lat = []
        self.indian_long = []
        for state in self.indian_states:
            temp = indian_lat_long[indian_lat_long["States"]==state]
            self.indian_lat.append(temp["Latitude"].values[0])
            self.indian_long.append(temp["Longitude"].values[0])
        self.select_states()
        
    def simulate_state(self, state, extra=0, plot=False):
        time_ref, cases_ref, deaths_ref, recovered_ref = self.selected_indian_data[state].values()
        if state in self.state_params:
            a, b, c = self.state_params[state]
        else:    
            a, b, c = self.state_simulator.fit_country(time_ref, cases_ref, recovered_ref, deaths_ref)
            self.state_params[state] = (a, b, c)
        time, sick, recovered, deaths = self.state_simulator.calculate_epidemic(len(time_ref)+extra, 1e5, cases_ref[0], a, b, c)
        time, sick, recovered, deaths = self.remove_fractions(time, sick, recovered, deaths)
        if plot:
            self.plot_states(state, time, sick, recovered, deaths)
        else:
            return time, sick, recovered, deaths
    
    def simulate_state_all(self, extra=60):
        self.all_simulated_states = {}
        for state in self.selected_indian_states:
            time_ref, _, _, _ = self.selected_indian_data[state].values()
            time, sick, _, _ = self.simulate_state(state, extra)
            days = self.convert_dates(time_ref[0], len(time))
            self.all_simulated_states[state] = {"days":days, "active":sick}
        with open('data/all_states.pickle', 'wb') as handle:
            pickle.dump(self.all_simulated_states, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    def load_states(self):
        with open('data/all_states.pickle', 'rb') as handle:
            self.all_simulated_states = pickle.load(handle)
    
    def plot_states(self, state, time, sick, recovered, deaths):
        time_ref, cases_ref, deaths_ref, recovered_ref = self.selected_indian_data[state].values()
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
    
if __name__ == "__main__":
    start = time.time()
    COVID = covid()
    # COVID.simulate_state("Delhi",0,True)
    # COVID.simulate_country("India", True, 60)
    COVID.fit_all(60)
    COVID.simulate_state_all(60)
    print(time.time() - start)