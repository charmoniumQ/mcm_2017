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

def strat_leader(t, dt, car, car_before, car_after, *args):
    if car_after is None:
        state, lane, a = strat_random(t, dt, car, car_before, car_after, *args)
        return 'strat_gipps', lane, a
    else:
        return strat_gipps(t, dt, car, car_before, car_after, *args)

def strat_gipps(t, dt, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after):
    s = car[t]
    s.theta = s.tau / 2
    s.B_hat = -3
    if car_after is None:
        a = (s.v_max - s.v) / dt
        return 'strat_gipps', 0, a
    else:
        a = car_after[t]
        # B tau theta S B_hat
        s.B = s.v**2 / (2 * (a.x - s.x - a.v**2 / (2*s.B_hat)))
        v_1 = -s.B * (s.tau / 2 + s.theta) + sqrt(max((s.B * (s.tau / 2 + s.theta))**2 + s.B * (2 * (a.x - s.x - s.S) - s.tau * s.v + a.v**2 / s.B_hat), 0))
        v_2 = s.v + 2.5 * s.A * s.tau * (1 - s.v / s.v_max) * max(0.025 + s.v / s.v_max, 0)**(1/2)
        a = (min(v_1, v_2) - s.v) / dt
        return 'strat_gipps', 0, a

# export strategies to dict
strategies = {name: val for name, val in locals().items()
              if name.startswith('strat')}
