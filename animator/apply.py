#!/usr/bin/env python3

import cProfile
import random
import json
from simulate import simulate, CarInstant
import itertools
from export import export_json as export

def build_lane(length, n_cars, v):
    first_car = CarInstant('strat_constant', 0, 0, 0, 0, mu=v, sigma=v / 10, p_lane_change=0, visible=True)
    middle_cars = [CarInstant('strat_idm', 0, 0, 0, 0, S=6.0, visible=True) for _ in range(n_cars - 1)]
    cars = middle_cars + [first_car]
    r =  randomly_place(cars, length, v)
    print(r[-1])
    r[-1].v = 20
    return r

def randomly_place(cars, length, v):
    '''Randomly place cars with a random gap (between gmin and gmax) with a
    random initial velocity (between vmin and vmax) both with uniform distribution'''
    for i, car in enumerate(cars):
        car.x = random.gauss(mu=length * (i / len(cars)), sigma=(length / len(cars)) / 10)
        car.v = random.gauss(mu=v, sigma=v / 10)
    return cars

def duplicate_time(cars, frames):
    '''
    cars: cars[which car] -> CarInstant
    returns: cars[which car][which frame] -> CarInstant'''
    return [[car.copy() for _ in range(frames)] for car in cars]

def build_road(length, n_cars, v, lanes, dt, frames, speedlimit):
    road = duplicate_time(list(itertools.chain.from_iterable(
        build_lane(length, n_cars, v) for lane in range(lanes)
    )), frames)
    simulate(road, lanes - 1, None, dt, speedlimit)
    export(road, length, dt)

if __name__ == '__main__':
    length = 4900
    lanes = 1
    dt = 0.1
    frames = 50
    speedlimit = 35
    q = 480 # cars / hour
    g = 6 # meters / car
    f = 1 / 3600 # hour / sec
    v = q * g * f # m / sec
    build_road(length, q, v, lanes, dt, frames, speedlimit)

# 4928 m
# 6260 cars / hour / lane
# 6 meters / car
