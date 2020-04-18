from scipy.optimize import fsolve
import math
import scipy.optimize
from scipy import interpolate

class simulate_epidemic:
    def __init__(self, init_mobility, init_recovery_probab, init_death_probab):
        self.init_mobility = init_mobility
        self.init_recovery_probab = init_recovery_probab
        self.init_death_probab = init_death_probab
        self.dt = 0.5
        self.healthy_n = 1e5
    
    def calculate_epidemic(self, t_final, healthy_n, infected_n, mobility, recovery_probab, death_probab):

        def infection_probab(mobility):
            return 0.4*mobility

        recovered_n = 0
        dead_n = 0

        def equations(state):
            H, I, R, D = state
            h = (H-healthy_n)/self.dt - (-infection_probab(mobility)*H*I)
            s = (I-infected_n)/self.dt - (infection_probab(mobility)*H*I - recovery_probab * I - death_probab*I)
            r = (R-recovered_n)/self.dt - (recovery_probab*I)
            m = (D-dead_n)/self.dt - (death_probab*I)
            return (h, s, r, m)

        time = []
        sick = []
        recovered = []
        deaths = []
        t = 0
        while t < t_final:
            t += self.dt
            H, I, R, D = fsolve(equations, (healthy_n, infected_n, recovered_n, dead_n))
            healthy_n, infected_n, recovered_n, dead_n = H, I, R, D

            time.append(t)
            sick.append(I)
            recovered.append(R)
            deaths.append(D)

        return time, sick, recovered, deaths
        
    
    def fit_country(self, time_ref, cases_ref, recovered_ref, deaths_ref):
        
        # the cost function
        def cost(initial_guess):
            (a, b, c) = initial_guess
            mobility = 10 ** (-a)
            recovery_probab = 10 ** (-b)
            death_probab = 10 ** (-c)

            time_sim, cases_sim, recovered_sim, deaths_sim = self.calculate_epidemic(len(time_ref), self.healthy_n, infected_n, mobility, recovery_probab, death_probab)
            interp_cases = interpolate.interp1d(time_sim, cases_sim, fill_value="extrapolate")
            interp_deaths = interpolate.interp1d(time_sim, deaths_sim, fill_value="extrapolate")
            interp_recovered = interpolate.interp1d(time_sim, recovered_sim, fill_value="extrapolate")

            c = 0
            time_number_days = [i for i in range(len(time_ref))]
            for i in range(len(time_number_days)):
                c = c + 5*(abs(deaths_ref[i] - interp_deaths(time_number_days[i])))
                c = c + 10*(abs(cases_ref[i] - interp_cases(time_number_days[i])))
                c = c + (abs(recovered_ref[i] - interp_recovered(time_number_days[i])))
            c = c/(3*(len(time_number_days)))
            return c


        infected_n = cases_ref[0]
        initial_guess = (self.init_mobility, self.init_recovery_probab, self.init_death_probab)
        res = scipy.optimize.minimize(cost, initial_guess, method = "Nelder-Mead")
        opt = res.x
        (a,b,c) = opt
        return 10**-a, 10**-b, 10**-c
        
        