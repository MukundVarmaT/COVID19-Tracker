from scipy.optimize import fsolve
import math


def calculate_epidemic(hosp_cap, mobility, t_final, healthy_n=1, infected_n=0.01, recovery_probab_init=1/(51-32),recovery_probab_minus=1/(51-32)/2, death_probab_init=0.02, death_probab_plus=0.01):
    '''
    Arguments:
    - hosp_cap: hospital capacity
    - mobility: People's mobility (0 means perfect confinement)
    - t_final: time of simulation
    '''
    dt = 5e-1

    def infection_probab(mobility):
        return 0.4*mobility

    def recovery_probab(I):
        if I < hosp_cap:
            return recovery_probab_init
        else:
            return recovery_probab_init - recovery_probab_minus

    def death_probab(I):
        if I < hosp_cap:
            return death_probab_init
        else:
            return death_probab_init + death_probab_plus

    rec_n = 0
    dead_n = 0

    def equations(state):
        H, I, R, D = state
        h = (H-healthy_n)/dt - (-infection_probab(mobility)*H*I)
        s = (I-infected_n)/dt - (infection_probab(mobility)*H*I - recovery_probab(I) * I - death_probab(I)*I)
        r = (R-rec_n)/dt - (recovery_probab(I)*I)
        m = (D-dead_n)/dt - (death_probab(I)*I)
        return (h, s, r, m)

    time = []
    sick = []
    healthy = []
    recovered = []
    deaths = []
    t = 0
    while t < t_final:
        t += dt
        H, I, R, D = fsolve(equations, (healthy_n, infected_n, rec_n, dead_n))
        healthy_n, infected_n, rec_n, dead_n = H, I, R, D

        time.append(t)
        sick.append(I)
        healthy.append(H)
        recovered.append(R)
        deaths.append(D)

    return time, sick, healthy, recovered, deaths