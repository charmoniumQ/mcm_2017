#!/usr/bin/env python3

import random
import json
from functools import partial
from simulate import simulate, CarInstant
from strategies import strategies
from util import project_dict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

cmap = cm.magma

def build_road(length, n_cars, v):
    cars = [CarInstant('strat_random', 0, 0, 0, 0, mu=v, sigma=v / 10, p_lane_change=0, visible=True)]
    randomly_place()
    pass

def randomly_place(cars, x_sigma, v_mu, v_sigma):
    '''Randomly place cars with a random gap (between gmin and gmax) with a
    random initial velocity (between vmin and vmax) both with uniform distribution'''
    for i, car in enumerate(cars):
        car.x = random.gauss(mu=length * (i / len(cars)), sigma=1.5)
        car.v = random.gauss(mu=v_mu, sigma=v_sigma)
    return cars

def gen_random():
    return CarInstant('strat_random', 0, 0, 0, 0, mu=2, sigma=10, p_lane_change=0.015, lane_change_margin=5, visible=True)

# http://www.sciencedirect.com/science/article/pii/0191261581900370
A = partial(random.gauss, mu=1.7, sigma=0.3)
tau = partial(random.gauss, mu=2/3, sigma=0.05)
S = partial(random.gauss, mu=6.5, sigma=0.3)
v_max = partial(random.gauss, mu=20, sigma=3.2)

def gen_gipps():
    return CarInstant('strat_gipps2', 0, 0, 0, 0, A=A(), tau=tau(), theta=tau() / 2, S=S(), v_max=v_max(), B_hat=-2 * A(), visible=True)

def birth_idm(frame, first_car):
    if False and first_car[frame].x > first_car[frame].gap:
        c = CarInstant('strat_idm', first_car[frame].lane, 0, first_car[frame].v, 0, S=S(), visible=True, birth=birth_idm)
        return c
    else:
        return None

def gen_idm():
    return CarInstant('strat_idm', 0, 0, 0, 0, S=S(), birth=birth_idm, visible=True)

def chain(n, lane):
    ''''Returns n strat_optimal cars sandwiched with strat_constant cars'''
    cars = [gen_idm() for _ in range(n)]
    for car in cars:
        car.lane = lane
    return cars

def duplicate_time(cars, frames):
    '''
    cars: cars[which car] -> CarInstant
    returns: cars[which car][which frame] -> CarInstant'''
    return [[car.copy() for _ in range(frames)] for car in cars]

linestyles = {
    'strat_optimal': '--',
    'strat_random': '-',
    'strat_gipps': '--',
    'strat_leader': '-',
    'strat_idm': '-',
}

def export(road, max_dist, dt):
    '''export data and graph for HTML viewer
    road: array as follows road[which car][which frame] -> CarInstant'''

    max_lane = max(car_instant.lane for car in road for car_instant in car)
    keys = {'x', 'i', 'state', 'visible', 'lane'}
    road_dict = [[project_dict(car_instant.as_dict(), keys) for car_instant in car] for car in road]

    with open('data.js', 'w') as f:
        f.write('const road = {};\n'.format(json.dumps(road_dict)))
        f.write('const max_x = {};\n'.format(max_dist))
        f.write('const max_lane = {};\n'.format(max_lane))
        f.write('const dt = {};\n'.format(dt))

        ts = np.arange(0, len(road[0])) * dt
        max_lane = max(cari.lane for car in road for cari in car)
        for lane in range(max_lane):
            pass

    for lane in range(max_lane + 1):
        print('exporting graph for lane {lane}'.format(**locals()))
        plt.figure(figsize=(4, 5))
        plt.ylim(0, max_dist)
        plt.xlim(0, len(road[0]) * dt)
        plt.xlabel('time')
        plt.ylabel('dist')
        for car in road:
            xs = []
            ts = []
            for frame, c in enumerate(car):
                if c.lane == lane and c.visible:
                    xs.append(c.x)
                    ts.append(frame * dt)
                else:
                    plt.plot(ts, xs, color=cmap(c.i / len(road)), linestyle=linestyles[car[0].state])
                    xs = []
                    ts = []
            else:
                plt.plot(ts, xs, color=cmap(c.i / len(road)), linestyle=linestyles[car[0].state])
        plt.savefig('lane_{lane}.png'.format(**locals()))

if __name__ == '__main__':
    g_range = (30, 50)
    v_range = (0, 20)
    frames = 100
    dt = 0.05
    speedlimit = 50
    lanes = 2
    max_dist = 200
    road = (
        duplicate_time(randomly_place(chain(3, 0), g_range, v_range), frames) +
        duplicate_time(randomly_place(chain(5, 1), g_range, v_range), frames) +
        duplicate_time(randomly_place(chain(7, 2), g_range, v_range), frames) +
        [])

    simulate(road, lanes, max_dist, dt, speedlimit, strategies)
    export(road, max_dist, dt)
