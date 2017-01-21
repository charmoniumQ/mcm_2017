#!/usr/bin/env python3

import random
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

def chain(n):
    ''''Returns n strat_optimal cars sandwiched with strat_constant cars'''
    CI = CarInstant
    return (
        [CI('strat_constant', 0, 30, 0)] +
        [CI('strat_optimal', 0, 30, 0) for _ in range(n)] +
        [CI('strat_constant', 0, 30, 0)])

def duplicate_time(cars, frames):
    '''
    cars: cars[which car] -> CarInstant
    returns: cars[which car][which frame] -> CarInstant'''
    return [[car.copy() for _ in range(frames)] for car in cars]

if __name__ == '__main__':
    g_range = (10, 20)
    v_range = (20, 40)
    frames = 10
    dt = 0.05
    speedlimit = 50
    road = [
        duplicate_time(randomly_place(chain(4), g_range, v_range), frames),
        duplicate_time(randomly_place(chain(8), g_range, v_range), frames),
        duplicate_time(randomly_place(chain(12), g_range, v_range), frames),
    ]

    simulate(road, dt, speedlimit, strategies)
    export(road, dt)
