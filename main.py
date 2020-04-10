import data
import epidemic
import scipy.optimize
from scipy import interpolate
import matplotlib.pyplot as plt


def fit_country(country, extra=0):
    
    def cost(inital_guess):
        (a, b, c) = inital_guess
        mobility = 10 ** (-a)
        recovery_probab = 10 ** (-b)
        death_probab = 10 ** (-c)
        
        time_sim, cases_sim, healthy_sim, recovered_sim, deaths_sim = epidemic.calculate_epidemic(hosp_cap = 0, mobility=mobility, healthy_n = healthy_n, infected_n = infected_n, t_final = max(time_number_days), recovery_probab_init= recovery_probab, recovery_probab_minus=0, death_probab_init= death_probab, death_probab_plus=0) 
        interp_cases = interpolate.interp1d(time_sim, cases_sim, fill_value="extrapolate")
        interp_deaths = interpolate.interp1d(time_sim, deaths_sim, fill_value="extrapolate")
        interp_recovered = interpolate.interp1d(time_sim, recovered_sim, fill_value="extrapolate")
        
        c = 0
        
        for i in range(len(time_number_days)):
            c = c + 5*(abs(deaths_ref[i] - interp_deaths(time_number_days[i])))
            c = c + 10*(abs(cases_ref[i] - interp_cases(time_number_days[i])))
            c = c + (abs(recovered_ref[i] - interp_recovered(time_number_days[i])))
            
        c = c/(3*(len(time_number_days)))
        
        # print("Fit Mean difference : " + str(c), end="/r")
        return c
    
    
    healthy_n = 1e5
    time, time_number_days, cases_ref, deaths_ref, recovered_ref = data.get_data(country)
    
    infected_n = cases_ref[0]
    inital_guess = (5, 1.9, 2)
    print("Fitting!.......")
    
    res = scipy.optimize.minimize(cost, inital_guess, method = "Nelder-Mead")
    opt = res.x
    print("-"*50)
    
    (a,b,c) = opt
    
    mobility = 10 ** (-a)
    recovery_probab = 10 ** (-b)
    death_probab = 10 ** (-c)
    
    print("Fit mean difference: " + "{:.2%}".format(res.fun))
    
    print("mobility = %.2e" % mobility)
    print("recovered_probab = %.2e" % recovery_probab)
    print("death_probab = %.2e" % death_probab)
    
    time_sim, cases_sim, healthy_sim, recovered_sim, deaths_sim = epidemic.calculate_epidemic(hosp_cap = 0, mobility=mobility, healthy_n = healthy_n, infected_n = infected_n, t_final = max(time_number_days) + extra, recovery_probab_init= recovery_probab, recovery_probab_minus=0, death_probab_init= death_probab, death_probab_plus=0) 
    return time_sim, cases_sim, healthy_sim, recovered_sim, deaths_sim

def plot(x1, y1, x2, y2, ylabel, legends, color):

    fig, ax = plt.subplots()
    plt.title(country)
    plt.ylabel(ylabel)
    plt.xlabel("Days")
    plt.fill_between(x1, 0, y1, facecolor=color, alpha=0.1)
    plt.plot(x1, y1, label=legends[0],
             color=color, zorder=1)
    plt.scatter(x2, y2, label=legends[1],
                color=color, zorder=3, edgecolors="white", s=40)
    plt.minorticks_on()
    ax.grid(which='minor', alpha=0.3)
    ax.grid(which='major', alpha=0.7)
    ax.set_axisbelow(True)
    plt.legend()


if __name__ == "__main__":
    country = "India"
    time, time_number_days, cases_ref, deaths_ref, recovered_ref = data.get_data(country)
    time_sim, cases_sim, healthy_sim, recovered_sim, deaths_sim = fit_country(country)
    print(time_sim)
    plot(time_sim, cases_sim, time_number_days, cases_ref,
             "Number of actives cases",
             ["Predicted cases", "Actual cases"],
             "tab:blue")
    plot(time_sim, deaths_sim, time_number_days, deaths_ref,
            "Cumulative number of deaths",
            ["Predicted deaths", "Actual number of deaths"],
            "tab:red")
    plot(time_sim, recovered_sim, time_number_days, recovered_ref,
            "Cumulative number of recovered",
            ["Predicted recovered", "Actual number of recovered"],
            "tab:green")

    plt.show()
    