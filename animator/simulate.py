import numpy as np
import matplotlib.pyplot as plt
import json
from util import zip_adj, DotDict

def check_mirror(frame, car, otherlane):
    '''looks over your shoulder to see who is there
    Returns (otherlane_car_backwards, otherlane_car_forwards)
    each of which could be None if no car is present'''

    if otherlane is None:
        return (None, None)

    for otherlane_car, next_otherlane_car in zip_adj(otherlane, 2, 1):
        if next_otherlane_car is None or next_otherlane_car[frame].x > car[frame].x:
            break
    return (otherlane_car, next_otherlane_car)

def normalize_a(frame, car, a, dt, speedlimit):
    '''Prevent cars from accelerating past speedlimit or decelerating past zero'''
    if speedlimit is not None and car[frame].v + a * dt > speedlimit:
        # accelerate exactly to speedlimit instead
        return (speedlimit - car[frame].v) / dt
    elif car[frame].v + a * dt < 0:
        # decelerate exactly to zero instead
        return car.v / dt
    else:
        return a

class CarInstant(DotDict):
    def __init__(self, state, x, v, a, **kwargs):
        DotDict.__init__(self, **kwargs)
        self.state, self.x, self.v, self.a = state, x, v, a

    def copy(self):
        return CarInstant(**self.as_dict())

    def kinematics(self):
        '''Packs kinematic variables into tuple (state, x, v, a)'''
        return (self.state, self.x, self.v, self.a)

def time_slice(frame, road):
    return [[car[frame] for car in lane] for lane in road]

def simulate(road, dt, speedlimit, strategies):
    '''
    road: array as follows road[which lane][which car][which frame] -> CarInstant
    dt: size of one frame
    frames: number of frames to simulate
    speedlimit: speed cap on cars
    strategies: dict as follows strategies[string] -> (function(frame, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after, dt) -> new_state, new_a)'''
    for frame in range(1, len(road[0][0])):
        for leftlane, lane, rightlane in zip_adj(road, 3, 1):
            for car_before, car, car_after in zip_adj(lane, 3, 1):
                car_left_before, car_left_after = check_mirror(frame, car, leftlane)
                car_right_before, car_right_after = check_mirror(frame, car, rightlane)
                state, x, v, a = car[frame - 1].kinematics()
                state, a = strategies[state](frame, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after, dt)
                normalize_a(frame, car, a, dt, speedlimit)
                car[frame].a = a
                car[frame].v = a * dt + v
                car[frame].x = a * dt**2 / 2 + v * dt + x
                car[frame].state = state

def export(road, dt):
    '''export data and graph for HTML viewer
    road: array as follows road[which lane][which car][which frame] -> CarInstant'''

    # cars: cars[which car][which frame] -> x
    cars = [[cari.x for cari in car] for lane in road for car in lane]
    # road:  road[which lane][which car][which frame] -> dict'''
    road = [[[car_instant.as_dict() for car_instant in car] for car in lane] for lane in road]
    maxX = max(xs for car in cars for xs in car)

    with open('data.js', 'w') as f:
        f.write('const road = {};\n'.format(json.dumps(road)))
        f.write('const maxX = {};\n'.format(maxX))
        f.write('const dt = {};\n'.format(dt))

    plt.figure(figsize=(5,5))
    plt.ylim(0, maxX)
    plt.xlim(0, len(road[0][0]) * dt)
    plt.xlabel('time')
    plt.ylabel('dist')
    ts = np.arange(0, len(road[0][0])) * dt
    for color, lane in zip('rgbcmyk', road):
        for car in lane:
            plt.plot(ts, [instant['x'] for instant in car], color=color)
            plt.savefig('output.png')
