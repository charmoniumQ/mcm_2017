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

def strat_random(frame, dt, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after):
    a = random.gauss(car[0].mu, car[0].sigma)
    lane = 0
    if random.uniform(0, 1) < car[0].p_lane_change:
        lane = random.choice([-1, 1])
        if lane == -1 and car_left_before is not None and (car[frame].x - car_left_before[frame].x) < car[0].lane_change_margin:
            lane = 0
        if lane == 1 and car_right_before is not None and (car[frame].x - car_right_before[frame].x) < car[0].lane_change_margin:
            lane = 0
    return 'strat_random', lane, a

# export strategies to dict
strategies = {name: val for name, val in locals().items()
              if name.startswith('strat')}
