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

# export strategies to dict
strategies = {name: val for name, val in locals().items()
              if name.startswith('strat')}
