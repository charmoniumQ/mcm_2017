from math import sqrt
import random

# strategy_x(frame, dt, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after) -> new_state, new_a
# where cars are car[frame number] -> DotDict with state, x, v, a

def strat_optimal(t, dt, s, b, f, lb, la, rb, ra):
    if None in (b, f):
        return 'strat_optimal', 0, 0
    else:
        a = (f[t].x + b[t].x - 2*s[t].x) / pow(dt,2) + (f[t].v + b[t].v - 2*s[t].v) / dt
        a /= 20
        return 'strat_optimal', 0, a

def strat_constant(*args):
    return 'strat_constant', 0, 0

def too_close(frame, car_a, car_b, tolerance):
    # mu, sigma, p_lane_change, lane_change_margin
    if car_a is not None and car_b is not None and abs(car_a[frame].x - car_b[frame].x) < tolerance:
        return True

def strat_random(frame, dt, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after):
    a = random.gauss(car[0].mu, car[0].sigma)
    lane = 0
    if random.uniform(0, 1) < car[0].p_lane_change:
        lane = random.choice([-1, 1])
        if lane == -1:
            if (too_close(frame, car, car_left_before, car[0].lane_change_margin) or
                too_close(frame, car, car_left_after, car[0].lane_change_margin)
            ):
                lane = 0 # cancel lane change
        if lane == 1:
            if (too_close(frame, car, car_right_before, car[0].lane_change_margin) or
                too_close(frame, car, car_right_after, car[0].lane_change_margin)
            ):
                lane = 0 # cancel lane change
    return 'strat_random', lane, a

def strat_gipps(t, dt, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after):
    n = car[t]
    if car_after is None:
        # leader
        a = (n.v_max - n.v) / dt
        return 'strat_gipps', 0, a
    else:
        n1 = car_after[t]
        # B tau theta S B_hat
        xp = (-n1.v**2 - 2 * n1.B_hat * n1.x) / (2 * n1.B_hat)
        xmid = n.x + n.v * (n.tau + n.theta)
        n.B = -n.v**2 / (2 * (xp - xmid - n.S)) # Tushar
        # n.B = n.v**2 / (2 * (n1.x - n.x + n1.v**2 / (2*n1.B_hat))) # Sam
        v_1 = n.v + 2.5 * n.A * n.tau * (1 - n.v / n.v_max) * sqrt(max(0.025 + n.v / n.v_max, 0))
        # v_1 = 100000 # Gipps with no accel
        # v_2 = -n.B * (n.tau / 2 + n.theta) + sqrt(max((n.B * (n.tau / 2 + n.theta))**2 + n.B * (2 * (n1.x - n.x - n.S) - n.tau * n.v + n1.v**2 / n1.B_hat), 0)) # Gipps 1
        v_2 = n.B * n.tau + sqrt(max((b.n * b.tau)**2 - b.n * (2 * (n1.x - n1.S - n.x) - n.v * n.tau - n1.v**2 / n1.B_hat))) # Gipps 2
        a = (min(v_1, v_2) - n.v) / dt
        return 'strat_gipps', 0, a

# http://www.sciencedirect.com/science/article/pii/0191261581900370
A = 1.7 # stddev = 0.3
B_hat = -1 * A
tau = 2/3
S = 6.5 # stddev = 0.3
V_max = 20 # stddev = 3.2
theta = tau / 2

def strat_gipps2(t, dt, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after):
    if car_after is None:
        return 'strat_gipps2', 0, 0
    else:
        s, a = car[t], car_after[t]
        # B tau theta S B_hat
        B = s.v**2 / (2 * (a.x - s.x + a.v**2 / (2*B_hat)))
        v_1 = -B * (tau / 2 + theta) + sqrt(max((B * (tau / 2 + theta))**2 + B * (2 * (a.x - s.x - S) - tau * s.v + a.v**2 / B_hat), 0))
        v_1 = 1000
        v_2 = s.v + 2.5 * A * tau * (1 - s.v / V_max) * (0.025 + s.v / V_max)**(1/2)
        v = min(v_1, v_2)
        a = (v - s.v) / dt
        return 'strat_gipps2', 0, a
v0 = 120.0 * 1000 / 3600
sigma = 4.0
T = 1.5
s0 = 2.0
A = 1.4 * 3.6
B = 2.0 * 3.6
C = 0.99

def strat_idm(t, dt, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after):
    if car_after is None:
        a = (v0 - car[t].v) / dt
        # _, lane, a = strat_random(t, dt, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after)
        return 'strat_idm', 0, a
    else:
        try:
            n = car[t]
            n1 = car_after[t]
            v = n.v
            vn1 = n1.v
            s = n1.x - n.x - n.S
            dv = v - vn1
            s_ = s0 + v * T + v * dv / (2 * sqrt(A * B))
            v / v0
            (v - v0)**sigma # throws exception
            s_ / s
            (s_ / s)**2
            p = 1 - (v / v0)**sigma - (s_ / s)**2
            a = A * p
            car[t + 1].gap = s_
            return 'strat_idm', 0, a
        except OverflowError:
            return 'strat_idm', 0, 0
            

# export strategies to dict
strategies = {name: val for name, val in locals().items()
              if name.startswith('strat')}
