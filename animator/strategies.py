# strategy_x(frame, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after, dt) -> new_state, new_a
# where cars are car[frame number] -> DotDict with state, x, v, a

def strat_optimal(t_, s, b, f, lb, la, rb, ra, dt):
    if None in (b, f):
        return 'strat_constant', 0
    else:
        t = t_ - 1 # so I don't have to retype t_ - 1 in the next line
        a = (f[t].x + b[t].x - 2*s[t].x) / pow(dt,2) + (f[t].v + b[t].v - 2*s[t].v) / dt
        a /= 10
        return 'strat_optimal', a

def strat_constant(*args):
    return 'strat_constant', 0

def strat_random(frame, car, *args):
    return 'strat_random', random.gauss(car[0].mu, car[0].sigma)

# export strategies to dict
strategies = {name: val for name, val in locals().items()
              if name.startswith('strat')}
