#!/usr/bin/env python3

import random
from functools import partial
from simulate import simulate, export, CarInstant
from strategies import strategies

def randomly_place(cars, g_range, v_range):
    '''Randomly place cars with a random gap (between gmin and gmax) with a
    random initial velocity (between vmin and vmax) both with uniform distribution'''
    cars[0].x = 0
    for car_b, car in zip(cars[:-1], cars[1:]):
        car.x = car_b.x + random.uniform(*g_range)
    for car in cars:
        car.v = random.uniform(*v_range)
    return cars

def gen_random():
    return CarInstant('strat_random', 0, 0, 0, 0, mu=2, sigma=10, p_lane_change=0.015, lane_change_margin=5)

# http://www.sciencedirect.com/science/article/pii/0191261581900370
A = partial(random.gauss, mu=1.7, sigma=0.3)
tau = partial(random.gauss, mu=2/3, sigma=0.05)
S = partial(random.gauss, mu=6.5, sigma=0.3)
v_max = partial(random.gauss, mu=20, sigma=3.2)

def gen_gipps():
    return CarInstant('strat_gipps2', 0, 0, 0, 0, A=A(), tau=tau(), theta=tau() / 2, S=S(), v_max=v_max(), B_hat=-2 * A())

def chain(n, lane):
    ''''Returns n strat_optimal cars sandwiched with strat_constant cars'''
    cars = [gen_gipps() for _ in range(n)]
    for car in cars:
        car.lane = lane
    return cars

def duplicate_time(cars, frames):
    '''
    cars: cars[which car] -> CarInstant
    returns: cars[which car][which frame] -> CarInstant'''
    return [[car.copy() for _ in range(frames)] for car in cars]

if __name__ == '__main__':
    g_range = (10, 20)
    v_range = (20, 40)
    frames = 1000
    dt = 0.01
    speedlimit = 50
    lanes = 2
    road = (
        duplicate_time(randomly_place(chain(3, 0), g_range, v_range), frames) +
        duplicate_time(randomly_place(chain(5, 1), g_range, v_range), frames) +
        duplicate_time(randomly_place(chain(7, 2), g_range, v_range), frames)
    )

    simulate(road, lanes, dt, speedlimit, strategies)
    export(road, dt)
